from enum import Enum, auto

from argg_hdl import *
from  argg_hdl.examples import *

from .helpers import Folders_isSame, vhdl_conversion, do_simulation,printf

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

class tx_sr_cl(Enum):
    idle = auto()
    sampleSelect= auto()
    clock_out_data= auto()
    received_data= auto()

class TX_shift_register_readout_slave(v_class_slave):
    def __init__(self,DataIn : TXShiftRegisterSignals):
        super().__init__()
        self.rx = variable_port_Slave(DataIn)
        self.rx << DataIn
        self.state = v_variable(v_enum(tx_sr_cl.idle))
        self.AsicN = v_variable( v_slv(4))
        self.counter   = v_variable( v_slv(32))
        self.sr_counter = v_variable( v_slv(32))
        self.sr_counter_max = v_variable( v_slv(32))
        self.sr_dataRead = v_variable(v_sl())

        self.RO_Config= v_variable(readOutConfig())

    def _onPull(self):
        self.counter << self.counter + 1
        self.rx.sr_select.reset()
        self.rx.sr_Clock.reset()
        self.sr_dataRead.reset()
        if self.state == tx_sr_cl.sampleSelect:
            if self.counter >= self.RO_Config.sr_select_start and self.counter <= self.RO_Config.sr_select_stop:
                self.rx.sr_select << 1
            
            if self.counter >= self.RO_Config.sr_clk_start and self.counter <= self.RO_Config.sr_clk_stop:
                self.rx.sr_Clock[self.AsicN] << 1
            if self.counter >= self.RO_Config.sr_select_done:
                self.state << tx_sr_cl.clock_out_data
                self.counter << self.RO_Config.sr_clk_High

        elif self.state == tx_sr_cl.clock_out_data:
            self.rx.SampleSelectAny[self.AsicN] << 1
      
            if self.counter < self.RO_Config.sr_clk_High:
                self.rx.sr_Clock[self.AsicN] << 1
        
            elif self.counter >= self.RO_Config.sr_clk_Period:
                self.state << tx_sr_cl.received_data
            
            
    def _onPush(self):
        if self.sr_dataRead:
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
        self.AsicN << AsicN; 
        self.rx.SampleSelectAny[self.AsicN] << 1
        self.counter.reset()
        self.sr_counter.reset()
        self.state << tx_sr_cl.sampleSelect


    def isEndOfStream(self):
        return True

    def __bool__(self):
        return self.state == tx_sr_cl.received_data

    def __rshift__(self, rhs):
        rhs << self.rx.data_out
        self.sr_dataRead << 1

class readOutConfig(v_record):
    def __init__(self, Name=None, varSigConst=None):
        super().__init__(Name=Name, varSigConst=varSigConst)
        self.sr_select_stop   = v_slv(8)
        self.sr_clk_Period    = v_slv(8)
        self.sr_clk_stop      = v_slv(8)
        self.sr_select_done   = v_slv(8)
        self.sr_select_start  = v_slv(8)
        self.sr_clk_High      = v_slv(8)
        self.sr_clk_start     = v_slv(8)

class tx_slro_st(Enum):
    idle = auto()
    running = auto()
    waiting_for_finish = auto()

class tx_sr_out(Enum):
    header0 = auto()
    header1 = auto()
    data = auto()
    footer = auto()

class SerialDataRoutProcess_cl(v_clk_entity):
    def __init__(self, clk=None):
        super().__init__(clk=clk)
        self.config_in        = port_Stream_Slave(axisStream(SerialDataConfig()))
        self.ShiftRegister_in = port_Slave(TXShiftRegisterSignals())
        self.data_out         = port_Stream_Master(axisStream(v_slv(32)))
        
        self.architecture()

    @architecture
    def architecture(self):

        state = v_signal(v_enum(tx_slro_st.idle))
        stateOut = v_signal(v_enum(tx_sr_out.header0))

        ConIn = get_handle(self.config_in)
        dataOut = get_handle(self.data_out)
        ConData = v_variable(SerialDataConfig())
        sample = v_variable(v_slv(5))
        header  = v_variable(v_slv(32))
        data = v_variable(self.ShiftRegister_in.data_out)
        data_prefix = v_variable(v_slv(12,0xDEF))

        shiftRegster = TX_shift_register_readout_slave(self.ShiftRegister_in)


        @rising_edge(self.clk)
        def proc():

            if state == tx_slro_st.idle:
                if ConIn:
                    ConIn >> ConData
                    sample << ConData.sample_start
            elif state == tx_slro_st.running:
                if shiftRegster.isReady2Request():
                    if ConData.force_test_pattern:
                        shiftRegster.request_test_Pattern(ConData.ASIC_NUM)
                        sample << ConData.sample_stop
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
                    stateOut << tx_sr_out.data
                elif  stateOut == tx_sr_out.data:
                    shiftRegster >> data
                    dataOut << (data_prefix & shiftRegster.sr_counter & data)

                elif  stateOut == tx_sr_out.footer:
                    dataOut << 0xFACEFACE
                    dataOut.Send_end_Of_Stream()
                    stateOut << tx_sr_out.header0

                if state == tx_slro_st.waiting_for_finish and shiftRegster.isEndOfStream():
                    state << tx_slro_st.idle
                    stateOut << tx_sr_out.footer


                



        end_architecture()



@vhdl_conversion
def TXReadout2vhdl(OutputPath):

    tb  =v_create(SerialDataRoutProcess_cl())
    return tb