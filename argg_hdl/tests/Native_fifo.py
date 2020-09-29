from argg_hdl import *
from  argg_hdl.examples import *

from .helpers import Folders_isSame, vhdl_conversion, do_simulation,printf


def dword():
    return v_slv(32)

class NativeFifoIn(v_class_trans):
    def __init__(self,DataType):
        super().__init__()
        self.enable  = port_out( v_sl()   )
        self.data    = port_out( DataType )
        self.full    = port_in ( v_sl()   )

class NativeFifoOut(v_class_trans):
    def __init__(self,DataType):
        super().__init__()
        self.empty    = port_out( v_sl()   )
        self.data     = port_out( DataType )
        self.enable   = port_in ( v_sl()   )
        
class NativeFifoInMaster(v_class_master):
    def __init__(self, Data):
        super().__init__()
        self.tx = variable_port_Master(Data)
        Data << self.tx 
        
    def _onPull(self):
        self.tx.enable << 0

    def ready_to_send(self):
        return self.tx.full == 0

    def send_data(self, data):
        self.tx.enable << 1
        self.tx.data   << data


class NativeFifoOutSlave(v_class_slave):
    def __init__(self, Data):
        super().__init__()

        
        self.rx1 = signal_port_Slave(Data)
        self.rx1 << Data
        self.rx = v_variable(Data)
        
        self.buff = small_buffer(Data.data)
        self.enable1 = v_variable(v_sl())
        self.empty1  = v_variable(v_sl())


    

    def _onPush_comb(self):
        if self.rx1.empty == 0:
            self.rx1.enable << self.rx.enable
        else:
            self.rx1.enable << 0
            
        self.rx.empty << self.rx1.empty
        self.rx.data << self.rx1.data  

        

    def _onPull(self):
        if self.enable1 and not self.empty1:
            self.buff << self.rx.data

        self.empty1 << self.rx.empty
        self.enable1 << self.rx.enable
        self.rx.enable << 0

    def _onPush(self):
        if not self.buff.isReceivingData():
            self.rx.enable << 1

    def isReceivingData(self):
        return self.buff.isReceivingData()

    def read_data(self, data):
        data.reset()
        self.buff >> data


class readout_native_fifo(v_entity):
    def __init__(self):
        super().__init__()
        self.clk = port_in(v_sl())
        self.Data_in = port_Slave(NativeFifoOut(v_slv(32)))
        self.architecture()
        
    @architecture
    def architecture(self):
        fifo_s = NativeFifoOutSlave(self.Data_in)
        data = v_slv(32)
        counter = dword()
        @rising_edge(self.clk)
        def proc():
            counter << counter +1
            if fifo_s.isReceivingData():
                fifo_s.read_data(data)

            printf("counter: " + str(value(counter)) + " data: " + str(value(data)) + "\n")


        end_architecture()


class fifo_cc_tb(v_entity):
    def __init__(self):
        super().__init__()
        self.architecture()


    @architecture
    def architecture(self):
        clkgen = clk_generator()
        ff_readout = readout_native_fifo()
        ff_readout.clk << clkgen.clk

        data = dword()
        @rising_edge(clkgen.clk)
        def proc():
            ff_readout.Data_in.empty << 1
            data << data +1
            if data > 10 and data < 20: 
                ff_readout.Data_in.empty << 0

            if ff_readout.Data_in.enable:
                ff_readout.Data_in.data << data

        end_architecture()

            


@do_simulation
def fifo_cc_tb_sim(OutputPath, f= None):
    
    tb1 = fifo_cc_tb()
    return tb1


@vhdl_conversion
def fifo_cc_tb_2vhdl(OutputPath, f= None):
    
    tb1 = fifo_cc_tb()
    return tb1
