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
        self.sr_counter = v_variable( v_slv(16))
        self.sr_counter_max = v_variable( v_slv(16,16))

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



class reg_entry(v_data_record):
    def __init__(self,addr = 0,data = 0):
        super().__init__()
        self.addr = v_slv(16,addr)
        self.data = v_slv(16,data)

    def get_register(self,reg):
        if reg.address == self.addr:
            self.data << reg.value

class SerialDataRoutProcess_cl_registers(v_data_record):
    def __init__(self):
        super().__init__()
        self.sr_select_min = reg_entry(100)
        self.sr_select_max = reg_entry(101)
        
        self.sr_clk_sampl_select_start =  reg_entry(102)
        self.sr_clk_sampl_select_stop  =  reg_entry(103)
        
        self.sr_header_start           =  reg_entry(104)
        self.sr_header_stop            =  reg_entry(105)
        
        self.sr_clk_high_start          =  reg_entry(106)
        self.sr_clk_high_stop           =  reg_entry(107)
        
        self.sr_clk_period              =  reg_entry(108)
    
        self.sr_clk_offset              =  reg_entry(109)


class SerialDataRoutProcess_cl(v_entity):
    def __init__(self, gSystem=None):
        super().__init__()
        self.gSystem = port_in(system_globals())
        if gSystem is not None:
            self.gSystem << gSystem

        self.config_in        = port_Stream_Slave(axisStream(SerialDataConfig()))
        self.ShiftRegister_in = port_Slave(TXShiftRegisterSignals())
        self.data_out         = port_Stream_Master(axisStream(v_slv(32)))
        self.data_out_raw     = port_out(v_slv(16))
        self.architecture()

    def get_clk(self):
        return self.gSystem.clk

    @architecture
    def architecture(self):
        gSystem123=system_globals()
        state = v_signal(v_enum(tx_slro_st.idle))
        stateOut = v_signal(v_enum(tx_sr_out.header0))

        ConIn       = get_handle(self.config_in)
        dataOut     = get_handle(self.data_out)
        ConData     = v_variable(SerialDataConfig())
        sample      = v_variable(v_slv(5))
        
        header      = v_const(v_slv(32,0xABCDABCD))
        data_prefix = v_const(v_slv(12,0xDEF))
        data_footer = v_const(v_slv(32,0xFACEFACE))

        registers_local = SerialDataRoutProcess_cl_registers()

        data        = v_variable(self.ShiftRegister_in.data_out)
        reg_readoutConfig = v_signal(readOutConfig())
        shiftRegster = TX_shift_register_readout_slave(self.ShiftRegister_in)

        self.data_out_raw << self.ShiftRegister_in.data_out

        @rising_edge(self.gSystem.clk)
        def proc():

           
            

            if state == tx_slro_st.idle and ConIn:
                shiftRegster.RO_Config << reg_readoutConfig
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

                


                
        @rising_edge(self.gSystem.clk)
        def proc_reg():
            registers_local.sr_select_min.get_register(self.gSystem.reg)
            registers_local.sr_select_max.get_register(self.gSystem.reg)
            
            

        end_architecture()



@vhdl_conversion
def TXReadout2vhdl(OutputPath):

    tb  =SerialDataRoutProcess_cl()
    return tb






class entity2FileConector():
    def __init__(self, DUT_entity, InputFileName,OutFileHandle, OutPutHeader):
        super().__init__()
        self.InputFileName = InputFileName
        self.DUT_entity = DUT_entity
        self.OutPutHeader = OutPutHeader
        self.OutFileHandle = OutFileHandle
        self.data = pd.read_csv(self.InputFileName )


        in_headers = [{"index": i, "name": x} for i,x in enumerate(self.data.columns)]
        self.readout_connections =self.make_connections2pandas(self.DUT_entity , in_headers, v_sl())

        out_headers = [{"index": i, "name": x} for i,x in enumerate(self.OutPutHeader.split(";"))]
        out_connections = self.make_connections2pandas(self.DUT_entity , out_headers, v_sl())
        self.out_connections = sorted(out_connections, key = lambda i: i['index']) 


    def do_IO(self, counter):
        if counter == 1:
            out_str = "Time "
            for x in self.out_connections:
                out_str +=   "; " + x["name"]
            out_str += "\n"
            self.OutFileHandle.write(out_str)
            
        for x in self.readout_connections:
            x["symbol"] <<  int(self.data.iloc[counter][x["name"]])
        
        out_str = str(counter) 
        for x in self.out_connections:
            out_str +=   "; " + str(value(x["symbol"]))
            
        out_str += "\n"
        self.OutFileHandle.write( out_str)
            
    def reduce_name(self, name,NameFragments):
        
        for x in NameFragments:
            name_sp = name.split(x.lower())
            if len(name_sp) > 1:
                name = name_sp[1]
            else:
                return ""

        return name
    

    def make_connections2pandas(self, hdl_obj,  pd_data_names,VetoClock, usedNameFragment=[]):
        


        ret = []
        for mem in hdl_obj.getMember():
            candidates = [x  for x in pd_data_names if  mem["name"].lower() in self.reduce_name(x["name"],usedNameFragment )]
            if not candidates:
                continue
            if type(mem["symbol"] ).__name__ == "v_symbol" and VetoClock is not mem["symbol"]:
                ret.append({
                    "name" : candidates[0]["name"],
                    'index' : candidates[0]["index"],
                    "symbol" : mem["symbol"]


                })
                print(usedNameFragment,mem["name"]," =>", candidates[0]["name"])
            else:
                con = self.make_connections2pandas(mem["symbol"], candidates, VetoClock, usedNameFragment + [ mem["name"] ] )
                ret += con

        return ret    



class TX_testbench(v_entity):
    def __init__(self, DUT_entity, InputFileName,OutFileHandle, OutPutHeader):
        super().__init__()
        self.IO =  entity2FileConector(
            DUT_entity = DUT_entity,
            InputFileName = InputFileName,
            OutFileHandle = OutFileHandle,
            OutPutHeader = OutPutHeader
        )
        self.DUT_entity = DUT_entity
        self.architecture()
        

    @architecture
    def architecture(self):
        readout = self.DUT_entity 
       

        clkgen = clk_generator()

        readout.get_clk()  << clkgen.clk


        counter = v_slv(32,1)
        

        

        @rising_edge(clkgen.clk)
        def proc():

            
            self.IO.do_IO(value( counter))
            counter << counter + 1

            
            

        end_architecture()

@do_simulation
def TXReadout_sim(OutputPath, f= None):
    with open("tests/targetx_sim/testcase2/header.txt") as fin:
        header = fin.readlines()[0]
        header = header.replace('"',"")
    
    DUT = SerialDataRoutProcess_cl()
    tb1 = TX_testbench(DUT, 
        InputFileName="tests/targetx_sim/testcase2/py_serialdataroutprocess_cl_tb_csv2.xlsm.csv",
        OutFileHandle= f,
        OutPutHeader = header
    )
    return tb1



