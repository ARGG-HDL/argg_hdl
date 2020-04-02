import argparse
import os,sys,inspect
from enum import Enum 
import copy 

from argg_hdl.argg_hdl_base import *
from argg_hdl.argg_hdl_v_Package import *
from argg_hdl.examples.klm_scrod_bus import *



Bitwidth = v_int(15,varSigConst=varSig.const_t)
asicN= v_slv(4)

class SerialDataConfig(v_class):
    def __init__(self):
        super().__init__("SerialDataConfig")
        self.__v_classType__       = v_classType_t.Record_t

        self.row_Select            = port_out( v_slv(3) )  
        self.column_select         = port_out( v_slv(6) )  
        self.ASIC_NUM              = port_out( asicN )  
        self.force_test_pattern    = port_out( v_sl() )  
        self.sample_start          = port_out( v_slv(5) )  
        self.sample_stop           = port_out( v_slv(5) )

   




class SerialDataRout_s_state(Enum):
    idle           = 0
    sampleSelect   = 1
    clock_out_data = 2
    received_data  = 3

class readOutConfig(v_class):
    def __init__(self):
        super().__init__("readOutConfig")
        self.__v_classType__   = v_classType_t.Record_t
        self.sr_select_start   = v_slv(8,0x04)
        self.sr_select_stop    = v_slv(8,0x10)
        self.sr_select_done    = v_slv(8,0x14)
        self.sr_clk_start      = v_slv(8,0x06)
        self.sr_clk_stop       = v_slv(8,0x09)

        self.sr_clk_High       = v_slv(8, 0x04 )
        self.sr_clk_Period     = v_slv(8, 0x09 )        
        
class SerialDataRout_s(v_class):
    def __init__(self):
        super().__init__("SerialDataRout_s")
        self.rx = port_Slave(TXShiftRegisterSignals())
        self.__v_classType__         = v_classType_t.Slave_t

        self.state  = v_enum(SerialDataRout_s_state.idle)

        self.counter   = v_slv(8)  #timing counter Handles for example the duration of the clk signal which gets send to TX
        
        self.AsicN             = v_int(0)
        self.sr_counter        = v_slv(8)
        self.sr_counter_max    = v_slv(8,12)
        self.sr_dataRead       = v_sl()
        self.RO_Config         = readOutConfig()



    def  request_sample(self,req_sample=port_in(v_slv(5)), AsicN = port_in(v_slv(4))):
        self.rx.SampleSelect << req_sample
        self.AsicN << AsicN
        self.rx.SampleSelectAny[self.AsicN] << 1

        self.counter << 0
        self.sr_counter << 0
        self.state << SerialDataRout_s_state.sampleSelect


    def request_test_Pattern(self,AsicN = port_in(v_slv(4))):
        self.AsicN <<  AsicN
        self.counter << 0
        self.sr_counter << 0
        self.state << SerialDataRout_s_state.sampleSelect

    def isReadyToRequestSample(self):
        return self.state == SerialDataRout_s_state.idle

    def isReceiving(self):
        return self.state ==  SerialDataRout_s_state.received_data; 

    def isEndOfStream(self):
        return self.isReceiving() and self.sr_counter == self.sr_counter_max ; 

    def read_data(self,data_out = port_out(v_slv(16))):
        data_out << self.rx.data_out
        self.sr_dataRead << 1

    def _onPull(self):
        self.counter << self.counter + 1
        self.rx.sr_select << 0
        self.rx.sr_Clock  << 0
        self.sr_dataRead  << 0
          


        if self.state == SerialDataRout_s_state.sampleSelect:
            if self.counter >= self.RO_Config.sr_select_start and self.counter <= self.RO_Config.sr_select_stop:
                self.rx.sr_select << 1
                
            if self.counter >= self.RO_Config.sr_clk_start  and self.counter <= self.RO_Config.sr_clk_stop:
                self.rx.sr_Clock[self.AsicN] << 1
                
                
            if  self.counter >= self.RO_Config.sr_select_done:
                    self.state << SerialDataRout_s_state.clock_out_data
                    self.counter << self.RO_Config.sr_clk_High
            
        elif  self.state == SerialDataRout_s_state.clock_out_data:
            self.rx.SampleSelectAny[self.AsicN] << 1
            if  self.counter < self.RO_Config.sr_clk_High:
                self.rx.sr_Clock[self.AsicN]  << 1

            elif  self.counter >= self.RO_Config.sr_clk_Period:
                self.state << SerialDataRout_s_state.received_data; 
                




    def _onPush(self):
        if self.sr_dataRead:
            self.sr_counter << self.sr_counter + 1
            self.state << SerialDataRout_s_state.clock_out_data
            self.counter << 0
        
        if self.sr_counter > self.sr_counter_max:
            self.state << SerialDataRout_s_state.idle
            self.sr_counter << 0
            self.rx.SampleSelect  << 0
            self.rx.SampleSelectAny  << 0



class TX_SamplingControls(v_class):
    def __init__(self):
        super().__init__("TX_SamplingControls")
        self.__v_classType__   = v_classType_t.Record_t
        self.WR_ADDRCLR     = v_sl()
        self.RD_ENA         = v_sl()
        self.RD_ROWSEL_S    = v_slv(3)
        self.RD_COLSEL_S    = v_slv(6)
        self.CLR            = v_sl()
        self.RAMP           = v_sl()


class TX_timeSpan(v_class):
    def __init__(self,Start=None,Stop=None):
        super().__init__("TX_timeSpan")
        self.__v_classType__   = v_classType_t.Record_t
        self.Start = v_slv(16)
        self.Stop  = v_slv(16)
        
        if Start:
            self.Start = v_slv(16,Start)
             
        if Stop:
            self.Stop  = v_slv(16,Stop)
        
        

class TX_SamplingConfigs(v_class):
    def __init__(self):
        super().__init__("TX_SamplingConfigs")
        self.__v_classType__   = v_classType_t.Record_t
        
        self.WR_ADDRCLR = TX_timeSpan()
        
        self.RD_ENA     = TX_timeSpan()

        self.RD_ROWSEL_S = TX_timeSpan()
        self.RD_COLSEL_S = TX_timeSpan()
        
        self.CLR         = TX_timeSpan()

        self.RAMP        = TX_timeSpan()



class TX_WaveFormRO(v_class):
    def __init__(self):
        pass



        

