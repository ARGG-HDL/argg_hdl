from enum import Enum, auto
import pandas as pd 
from argg_hdl import *
from  argg_hdl.examples import *

from .helpers import Folders_isSame, vhdl_conversion, do_simulation,printf, printff


def sr_clk_t(val=0):
    return v_slv(8,val)

class TXShiftRegisterSignals(v_class_trans):
    def __init__(self):
        super().__init__()
        self.data_out         = port_out( v_slv(16) )  # one bit per Channel
        
        #sr = Shift Register 
        self.sr_clear         = port_in( v_sl() )
        self.sr_Clock         = port_in( v_slv(5) )
        self.sr_select        = port_in( v_sl() )

        self.SampleSelect     = port_in( v_slv(5) )
        self.SampleSelectAny  = port_in( v_slv(5) )


class SerialDataConfig(v_record):
    def __init__(self):
        super().__init__()

        self.row_Select            =  v_slv(3)   
        self.column_select         =  v_slv(6)   
        self.ASIC_NUM              =  v_slv(4)   
        self.force_test_pattern    =  v_sl()  
        self.sample_start          =  v_slv(5)   
        self.sample_stop           =  v_slv(5) 

class span_t(v_data_record):
    def __init__(self, start  , stop ):
        super().__init__()
        self.start  = sr_clk_t(start)
        self.stop   = sr_clk_t(stop)
    
    def isInRange(self,counter):
        return self.start <= counter and counter <= self.stop

    def isBeforeRange(self, counter):
        return counter < self.start

    def isAfterRange(self, counter):
        return self.stop < counter 

class tx_sr_cl(Enum):
    idle = auto()
    sampleSelect= auto()
    clock_out_data= auto()
    received_data= auto()
    data_was_read= auto()

class TX_shift_register_readout_slave(v_class_slave):
    def __init__(self,DataIn : TXShiftRegisterSignals):
        super().__init__()
        self.rx = variable_port_Slave(DataIn)
        self.rx << DataIn
        self.state = v_variable(v_enum(tx_sr_cl.idle))
        self.AsicN = v_variable( v_slv(4))
        self.counter   = v_variable( sr_clk_t() )
        self.sr_counter = v_variable( v_slv(32))
        self.sr_counter_max = v_variable( v_slv(32,16))

        self.RO_Config= v_variable(readOutConfig())

    def _onPull(self):
        if self.state == tx_sr_cl.idle:
            self.counter.reset()

        self.counter << self.counter + 1
        self.rx.sr_select.reset()
        self.rx.sr_Clock.reset()
        if self.state == tx_sr_cl.sampleSelect:
            if self.RO_Config.sr_select.isInRange(self.counter):
                self.rx.sr_select << 1
            
            if self.RO_Config.sr_clk_sampl_select.isInRange(self.counter):
                self.rx.sr_Clock[self.AsicN] << 1
            if not self.RO_Config.sr_header.isInRange(self.counter):
                self.state << tx_sr_cl.clock_out_data
                self.counter << self.RO_Config.sr_clk_high.stop

        elif self.state == tx_sr_cl.clock_out_data:
            self.rx.SampleSelectAny[self.AsicN] << 1
      
            if self.RO_Config.sr_clk_high.isInRange(self.counter):
                self.rx.sr_Clock[self.AsicN] << 1
        
            elif self.counter <= self.RO_Config.sr_clk_offset:
                self.state << tx_sr_cl.received_data
            
            
    def _onPush(self):
        if self.state == tx_sr_cl.data_was_read and  self.RO_Config.sr_clk_period <= self.counter:
            self.sr_counter << self.sr_counter + 1
            self.state << tx_sr_cl.clock_out_data
            self.counter << 0
  
        
  
        if self.sr_counter > self.sr_counter_max:
            self.state << tx_sr_cl.idle
            self.sr_counter.reset()
            self.rx.SampleSelect.reset()
            self.rx.SampleSelectAny.reset()
  
        


    def isReady2Request(self):
        return self.state == tx_sr_cl.idle

    def request_test_Pattern(self, AsicN):
        self.AsicN << AsicN
        self.counter.reset()
        self.sr_counter.reset()
        self.state << tx_sr_cl.sampleSelect

    def request_sample(self ,req_sample , AsicN):
        self.rx.SampleSelect << req_sample
        self.AsicN << AsicN
        self.rx.SampleSelectAny[self.AsicN] << 1
        self.counter.reset()
        self.sr_counter.reset()
        self.state << tx_sr_cl.sampleSelect


    def isEndOfStream(self):
        return self.sr_counter == self.sr_counter_max

    def __bool__(self):
        return self.state == tx_sr_cl.received_data or self.state == tx_sr_cl.data_was_read 

    def __rshift__(self, rhs):
        rhs << self.rx.data_out
        self.state << tx_sr_cl.data_was_read 

class readOutConfig(v_record):
    def __init__(self, Name=None, varSigConst=None):
        super().__init__(Name=Name, varSigConst=varSigConst)
        self.sr_select             = span_t(5,10)
        self.sr_clk_sampl_select   = span_t(7,8)
        self.sr_header             = span_t(0,20)
        self.sr_clk_high           = span_t(0,1)
        self.sr_clk_period         = sr_clk_t(2)
        self.sr_clk_offset         = sr_clk_t(2)


class tx_slro_st(Enum):
    idle = auto()
    running = auto()
    waiting_for_finish = auto()

class tx_sr_out(Enum):
    header0 = auto()
    header1 = auto()
    processdata = auto()
    footer = auto()

class SerialDataRoutProcess_cl(v_clk_entity):
    def __init__(self, clk=None):
        super().__init__(clk=clk)
        self.config_in        = port_Stream_Slave(axisStream(SerialDataConfig()))
        self.ShiftRegister_in = port_Slave(TXShiftRegisterSignals())
        self.data_out         = port_Stream_Master(axisStream(v_slv(32)))
        self.data_out_raw     = port_out(v_slv(16))
        self.architecture()

    @architecture
    def architecture(self):

        state = v_signal(v_enum(tx_slro_st.idle))
        stateOut = v_signal(v_enum(tx_sr_out.header0))

        ConIn = get_handle(self.config_in)
        dataOut = get_handle(self.data_out)
        ConData = v_variable(SerialDataConfig())
        sample = v_variable(v_slv(5))
        header  = v_variable(v_slv(32,0xABCDABCD))
        data = v_variable(self.ShiftRegister_in.data_out)
        data_prefix = v_variable(v_slv(12,0xDEF))
        data_footer = v_variable(v_slv(32,0xFACEFACE))

        shiftRegster = TX_shift_register_readout_slave(self.ShiftRegister_in)

        self.data_out_raw << self.ShiftRegister_in.data_out

        @rising_edge(self.clk)
        def proc():

            if state == tx_slro_st.idle and ConIn:
                ConIn >> ConData
                sample << ConData.sample_start
                state << tx_slro_st.running
            elif state == tx_slro_st.running and shiftRegster.isReady2Request():
                if ConData.force_test_pattern:
                    shiftRegster.request_test_Pattern(ConData.ASIC_NUM)
                    state << tx_slro_st.waiting_for_finish
                else:
                    shiftRegster.request_sample(sample, ConData.ASIC_NUM)
                    if sample == ConData.sample_stop:
                        state << tx_slro_st.waiting_for_finish
                    
                    sample << sample + 1    
                        
                


            
            if shiftRegster and dataOut:
                if stateOut == tx_sr_out.header0:
                    dataOut << header
                    stateOut << tx_sr_out.header1
                elif  stateOut == tx_sr_out.header1:
                    dataOut << header
                    stateOut << tx_sr_out.processdata
                elif  stateOut == tx_sr_out.processdata:
                    shiftRegster >> data
                    dataOut << (shiftRegster.sr_counter & data)
                    if state == tx_slro_st.waiting_for_finish and shiftRegster.isEndOfStream():
                        state << tx_slro_st.idle
                        stateOut << tx_sr_out.footer

            if dataOut and  stateOut == tx_sr_out.footer:
                dataOut << data_footer
                dataOut.Send_end_Of_Stream()
                stateOut << tx_sr_out.header0

                


                



        end_architecture()



@vhdl_conversion
def TXReadout2vhdl(OutputPath):

    tb  =v_create(SerialDataRoutProcess_cl())
    return tb



class TX_testbench(v_entity):
    def __init__(self):
        super().__init__()
        self.pd =  pd.DataFrame(columns=["Time","shiftregister_in_s2m_sr_clock", "shiftregister_in_s2m_sampleselectany", "shiftregister_in_s2m_sr_select", "shiftregister_in_s2m_sampleselect", "shiftregister_in_s2m_sr_clear", "shiftregister_in_m2s_data_out", "config_in_s2m_ready", "config_in_m2s_data_column_select", "config_in_m2s_data_sample_stop", "config_in_m2s_data_force_test_pattern", "config_in_m2s_data_row_select", "config_in_m2s_data_sample_start", "config_in_m2s_data_asic_num", "config_in_m2s_last", "config_in_m2s_valid", "data_out_s2m_ready", "data_out_m2s_data", "data_out_m2s_last", "data_out_m2s_valid", "data_out_raw"])
        self.architecture()
        

    @architecture
    def architecture(self):
        data = pd.read_csv("tests/targetx_sim/testcase/py_serialdataroutprocess_cl_tb_csv.xlsm.csv")

        clkgen = v_create(clk_generator())
        readout = v_create(SerialDataRoutProcess_cl(clkgen.clk))
        configIn = get_handle(readout.config_in)
        config = v_variable(SerialDataConfig())
        counter = v_slv(32,1)

        @rising_edge(clkgen.clk)
        def proc():
            if counter == 1:
                printf("Time ; shiftregister_in_s2m_sr_clock; shiftregister_in_s2m_sampleselectany; shiftregister_in_s2m_sr_select; shiftregister_in_s2m_sampleselect; shiftregister_in_s2m_sr_clear; shiftregister_in_m2s_data_out; config_in_s2m_ready; config_in_m2s_data_column_select; config_in_m2s_data_sample_stop; config_in_m2s_data_force_test_pattern; config_in_m2s_data_row_select; config_in_m2s_data_sample_start; config_in_m2s_data_asic_num; config_in_m2s_last; config_in_m2s_valid; data_out_s2m_ready; data_out_m2s_data; data_out_m2s_last; data_out_m2s_valid; data_out_raw\n")
            readout.ShiftRegister_in.data_out           << int(data.iloc[value(counter)]["shiftregister_in_m2s_data_out"])
            readout.config_in.data.column_select        << int(data.iloc[value(counter)]["config_in_m2s_data_column_select"])
            readout.config_in.data.sample_stop          << int(data.iloc[value(counter)]["config_in_m2s_data_sample_stop"])
            readout.config_in.data.force_test_pattern   << int(data.iloc[value(counter)]["config_in_m2s_data_force_test_pattern"])
            readout.config_in.data.row_Select           << int(data.iloc[value(counter)]["config_in_m2s_data_row_select"])
            readout.config_in.data.sample_start         << int(data.iloc[value(counter)]["config_in_m2s_data_sample_start"])
            readout.config_in.data.ASIC_NUM             << int(data.iloc[value(counter)]["config_in_m2s_data_asic_num"])
            readout.config_in.last                      << int(data.iloc[value(counter)]["config_in_m2s_last"])
            readout.config_in.valid                     << int(data.iloc[value(counter)]["config_in_m2s_valid"])
            readout.data_out.ready                      << int(data.iloc[value(counter)]["data_out_s2m_ready"])
            
            
            printff(
                counter,
                readout.ShiftRegister_in.sr_Clock,
                readout.ShiftRegister_in.SampleSelectAny,
                readout.ShiftRegister_in.sr_select,
                readout.ShiftRegister_in.SampleSelect,
                readout.ShiftRegister_in.sr_clear,
                readout.ShiftRegister_in.data_out,
                readout.config_in.ready,
                readout.config_in.data.column_select,
                readout.config_in.data.sample_stop,
                readout.config_in.data.force_test_pattern,
                readout.config_in.data.row_Select,
                readout.config_in.data.sample_start,
                readout.config_in.data.ASIC_NUM,
                readout.config_in.last,
                readout.config_in.valid,
                readout.data_out.ready,
                readout.data_out.data,
                readout.data_out.last,
                readout.data_out.valid,
                readout.data_out_raw
            )
            
            counter << counter + 1
            

        end_architecture()

@do_simulation
def TXReadout_sim(OutputPath, f= None):
    
    tb1 = v_create(TX_testbench())
    return tb1
