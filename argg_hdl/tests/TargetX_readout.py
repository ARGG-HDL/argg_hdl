from enum import Enum, auto
import pandas as pd 
from argg_hdl import *
from  argg_hdl.examples import *

from .helpers import Folders_isSame, vhdl_conversion, do_simulation,printf, printff


class register_addr:
    clr_start = 10
    clr_stop  = 11
    read_enable_start = 12
    read_enable_stop  = 13
    ramp_start = 14
    ramp_stop  = 15
    
    row_select_start = 16
    row_select_stop  = 17

    column_select_start = 18
    column_select_stop  = 19

    cntr_max_time  = 20

    wr_send_data_start = 21 
    wr_send_data_stop  = 22

    trigger_time_start  = 23
    trigger_time_stop   = 24
    
    wr_counter_max   = 25
    
    WR_enable_start  = 26
    WR_enable_stop   = 27
    

class TX_write_handler_signals(v_class_trans):
    def __init__(self):
        super().__init__()
        self.clear = port_out(v_sl())
        self.writeEnable_1   = port_out(v_slv(5))
        self.writeEnable_2   = port_out(v_slv(5))
        self.dummy   = port_in(v_slv(5))
        

class Trigger_bits_trigger(v_class_trans):
    def __init__(self):
        super().__init__()
        self.ctime    = port_out(v_slv(27))
        self.dummy   = port_in(v_slv(5))


class TX_write_handler(v_entity):
    def __init__(self, gSystem ):
        super().__init__()
        self.gSystem            =  port_in(gSystem)
        self.gSystem            << gSystem 
        #self.trigger_bits_in    =  port_Stream_Slave(axisStream(Trigger_bits_trigger()))
        self.config_in          =  port_Stream_Slave(axisStream(SerialDataConfig()))
        self.config_out         =  port_Stream_Master(axisStream(SerialDataConfig()))
        self.TX_signals         =  port_Master(TX_write_handler_signals())
        self.trigger            =  port_out(v_sl())

        self.architecture()



    @architecture
    def architecture(self):

        cnt = counter(16)
        rx = get_handle(self.config_in)
        tx = get_handle(self.config_out)
        WR_enable   = span_t(0,0)       
        clr_time    = span_t(0,0)       
        send_data_time  = span_t(0,0)       
        trigger_time    = span_t(0,0)       
        WR_en = v_slv(5)
        

        cnt_max = sr_clk_t()
        send_data = v_sl()

        @rising_edge(self.gSystem.clk)
        def proc():
            WR_en << 31
            if cnt.isReady() and rx:
                cnt.StartCountTo(cnt_max)

            if cnt.isDone() and rx:
                cnt.reset()
            
            if send_data and rx and tx:
                rx >> tx
            send_data << cnt.InTimeWindowSl_r(send_data_time)

            self.trigger   << cnt.InTimeWindowSl_r(trigger_time)
            
            self.TX_signals.clear           << cnt.InTimeWindowSl_r(clr_time)
            self.TX_signals.writeEnable_1   << cnt.InTimeWindowSLV_r(WR_enable,WR_en)
            self.TX_signals.writeEnable_2   << cnt.InTimeWindowSLV_r(WR_enable,WR_en)


        rh = register_handler(self.gSystem)
        WR_enable.start      << rh.get_register(register_addr.WR_enable_start)
        WR_enable.stop       << rh.get_register(register_addr.WR_enable_stop)

        clr_time.start       << rh.get_register(register_addr.clr_start)
        clr_time.stop        << rh.get_register(register_addr.clr_stop)
        
        send_data_time.start << rh.get_register(register_addr.wr_send_data_start)
        send_data_time.stop  << rh.get_register(register_addr.wr_send_data_stop)

        trigger_time.start   << rh.get_register(register_addr.trigger_time_start)
        trigger_time.stop    << rh.get_register(register_addr.trigger_time_stop)
        cnt_max              << rh.get_register(register_addr.wr_counter_max)

        end_architecture()

class TX_write_handler_tb(v_entity):
    def __init__(self ):
        super().__init__()
        self.architecture()



    @architecture
    def architecture(self):
        clk = clk_generator()
        regStorage = register_storage(clk.clk)
        gSystem = system_globals()
        gSystem  << regStorage.gSystem
        count = v_slv(32)
        dut = TX_write_handler(gSystem)
        tx = get_handle(dut.config_in)
        rx = get_handle(dut.config_out)
        buffer1 = get_buffer(dut.config_in)
        buffer2 = get_buffer(dut.config_in)

        @rising_edge(gSystem.clk)
        def proc():
            count<<count+1
            buffer1.ASIC_NUM << 1
            buffer1.column_select << 1
            buffer1.row_Select  << 1
            if count == 10:
                tx << buffer1

            rx >> buffer2


        regStorage.set_register(register_addr.WR_enable_start,10)
        regStorage.set_register(register_addr.WR_enable_stop, 20)
        regStorage.set_register(register_addr.wr_counter_max,200)
        regStorage.set_register(register_addr.clr_start,10)

        regStorage.set_register(register_addr.wr_send_data_start, 100)
        regStorage.set_register(register_addr.wr_send_data_stop ,200)        
        
        end_architecture()

@do_simulation
def TX_write_handler_tb_sim(OutputPath, f= None):
    tb = TX_write_handler_tb()
    return tb

@vhdl_conversion
def  TX_write_handler2vhdl(OutputPath):
    gSystem = system_globals()
    tb1 =  TX_write_handler_tb()
    tb  =SerialDataRoutProcess_cl()
    return tb1


############################################################################################################################
    
class TX_sampling_signals(v_class_trans):
    def __init__(self):
        super().__init__()
        self.clr = port_out(v_sl())
        self.read_enable   = port_out(v_sl())
        self.ramp          = port_out(v_sl())
        self.row_select    = port_out(v_slv(32))
        self.column_select = port_out(v_slv(32))

class TX_sampling_times(v_record):
    def __init__(self):
        super().__init__()
        self.clr             = span_t(5,10)        
        self.read_enable     = span_t(5,10)        
        self.ramp            = span_t(5,10)        
        self.row_select      = span_t(5,10)    
        self.column_select   = span_t(5,10)  

class TX_sampling_controller(v_entity):
    def __init__(self, gSystem=None):
        super().__init__()
        self.gSystem = port_in(system_globals())
        if gSystem is not None:
            self.gSystem << gSystem
        
        self.sampling_signals = port_Master(TX_sampling_signals())
        self.config_in        = port_Stream_Slave (axisStream(SerialDataConfig()))
        self.config_out       = port_Stream_Master(axisStream(SerialDataConfig()))

    
        self.architecture()



    @architecture
    def architecture(self):
        cnt = counter(16)
        rx = get_handle(self.config_in)
        tx = get_handle(self.config_out)
        buffer = get_buffer(self.config_in)
        endOfStream = v_bool()
        sampling_times = TX_sampling_times()

        max_cntr = v_slv(16)

        @rising_edge(self.gSystem.clk)
        def proc():
            if rx and cnt.isReady():
                rx >> buffer
                endOfStream << rx.IsEndOfStream()
                if buffer.force_test_pattern == 0:
                    cnt.StartCountTo(max_cntr)
                else:
                    cnt.StartCountTo(0)
                
            if tx and cnt.isDone():
                tx << buffer 
                tx.Send_end_Of_Stream(endOfStream)
                cnt.reset()

            

            self.sampling_signals.clr            << cnt.InTimeWindowSl_r(sampling_times.clr)
            self.sampling_signals.read_enable    << cnt.InTimeWindowSl_r(sampling_times.read_enable)
            self.sampling_signals.read_enable    << cnt.InTimeWindowSl_r(sampling_times.read_enable)
            self.sampling_signals.ramp           << cnt.InTimeWindowSl_r(sampling_times.ramp)
            
            
            self.sampling_signals.row_select        << cnt.InTimeWindowSLV_r(sampling_times.row_select,buffer.row_Select)
            self.sampling_signals.column_select     << cnt.InTimeWindowSLV_r(sampling_times.column_select,buffer.column_select)
            
         
        rh = register_handler(self.gSystem)
        sampling_times.clr.start << rh.get_register(register_addr.clr_start)
        sampling_times.clr.stop  << rh.get_register(register_addr.clr_stop)

        sampling_times.ramp.start << rh.get_register(register_addr.ramp_start)
        sampling_times.ramp.stop  << rh.get_register(register_addr.ramp_stop)

        sampling_times.row_select.start << rh.get_register(register_addr.row_select_start)
        sampling_times.row_select.stop  << rh.get_register(register_addr.row_select_stop)

        sampling_times.column_select.start << rh.get_register(register_addr.column_select_start)
        sampling_times.column_select.stop  << rh.get_register(register_addr.column_select_stop)

        sampling_times.read_enable.start << rh.get_register(register_addr.read_enable_start)
        sampling_times.read_enable.stop  << rh.get_register(register_addr.read_enable_stop)       
        

        max_cntr <<  rh.get_register(register_addr.cntr_max_time)       

        end_architecture()



class TX_sampling_controller_tp(v_entity):
    def __init__(self):
        super().__init__()
        self.architecture()

    @architecture
    def architecture(self):
        clk = clk_generator()
        regStorage = register_storage(clk.clk)
        gSystem = system_globals()
        gSystem  << regStorage.gSystem
        dut = TX_sampling_controller(gSystem)
        count = v_slv(32)
        tx = get_handle(dut.config_in)
        rx = get_handle(dut.config_out)
        buffer = get_buffer(dut.config_in)
        buffer2 = get_buffer(dut.config_in)

        regStorage.set_register(register_addr.clr_start,10)
        regStorage.set_register(register_addr.clr_stop,11)

        regStorage.set_register(register_addr.ramp_start,12)
        regStorage.set_register(register_addr.ramp_stop,13)

        regStorage.set_register(register_addr.row_select_start,14)
        regStorage.set_register(register_addr.row_select_stop,15)

        regStorage.set_register(register_addr.column_select_start,16)
        regStorage.set_register(register_addr.column_select_stop,17)

        regStorage.set_register(register_addr.read_enable_start,18)
        regStorage.set_register(register_addr.read_enable_stop,19)
        regStorage.set_register(register_addr.cntr_max_time, 30)

        @rising_edge( clk.clk )
        def proc():
            count << count + 1
            buffer.column_select << 1
            buffer.row_Select << 1
            if count == 20:
                tx << buffer

            if rx:
                rx >> buffer2

        
    
        end_architecture()


@do_simulation
def TX_sampling_controller_sim(OutputPath, f= None):
    tb = TX_sampling_controller_tp()
    return tb

##################################################################################################################################
def sr_clk_t(val=0):
    return v_slv(16,val)

def dword(val=0):
    return v_slv(32,val)

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
        return self.state == tx_sr_cl.received_data 

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
        self.sr_select_min = sr_clk_t(100)
        self.sr_select_max = sr_clk_t(101)
        
        self.sr_clk_sampl_select_start =  sr_clk_t(102)
        self.sr_clk_sampl_select_stop  =  sr_clk_t(103)
        
        self.sr_header_start           =  sr_clk_t(104)
        self.sr_header_stop            =  sr_clk_t(105)
        
        self.sr_clk_high_start          =  sr_clk_t(106)
        self.sr_clk_high_stop           =  sr_clk_t(107)
        
        self.sr_clk_period              =  sr_clk_t(108)
    
        self.sr_clk_offset              =  sr_clk_t(109)


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

                


        rh = register_handler(self.gSystem)

        t1 = v_slv(16)
        t1 << rh.get_register(123)

        a2 = v_slv(16,456)
        t2 = v_slv(16)
        t2 << rh.get_register(a2)


        end_architecture()



@vhdl_conversion
def TXReadout2vhdl(OutputPath):
    tb1 = TX_sampling_controller(system_globals())
    tb  =SerialDataRoutProcess_cl()
    return tb1






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

        readout.gSystem.clk << clkgen.clk


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


def get_buffer( axi ) -> SerialDataConfig:
    return v_variable(axi.data)
