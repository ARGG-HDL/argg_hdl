from argg_hdl import *
from  argg_hdl.examples import *

from .helpers import Folders_isSame, vhdl_conversion, do_simulation,printf
#tb3 = InputDelay_tb()
#convert_to_hdl(tb3, "pyhdl_waveform")





class ram_handler(v_class_trans):
    def __init__(self, DataType = v_slv(32) , AddressType = v_slv(32)):
        super().__init__()
        self.write_enable  = port_out(v_sl())
        self.Write_address = port_out(AddressType)
        self.Write_Data    = port_out(DataType)
        
        self.read_address  = port_out(AddressType)
        self.read_data     = port_in(DataType)


class addr_data(v_record):
    def __init__(self, DataType = v_slv(32) , AddressType = v_slv(32)):
        super().__init__()
        self.address  = v_copy(AddressType)
        self.data     = v_copy(DataType)
    
    def reset(self):
        self.address.reset()
        self.data.reset()


class ram_handle_master(v_class_master):
    def __init__(self, RamHandler):
        super().__init__()
        self.tx = variable_port_Master(RamHandler)
        RamHandler << self.tx
        self.addr  = v_variable(v_list(self.tx.read_address, 3))
        self.buff = small_buffer(addr_data())
        self.c_data = v_variable(addr_data())
        self.data_requested = v_variable(v_sl())

    def _onPull(self):
        self.tx.write_enable << 0
        for xasdsadads in range(len(self.addr) - 1):
            self.addr[xasdsadads] << self.addr[xasdsadads+1]

        self.addr[2] << 0
        self.data_requested << 0
        
        self.c_data.address << self.addr[0]
        self.c_data.data << self.tx.read_data
        self.buff << self.c_data

    def _onPush(self):
        if self.data_requested == 0:
            self.addr[2] << self.addr[1] + 1
        
        if self.addr[2] > 9:
            self.addr[2] << 0
        self.tx.read_address << self.addr[2]

    def ready_to_send(self):
        return self.tx.write_enable == 0

    def send_data(self, adr, data):
        self.tx.write_enable   << 1
        self.tx.Write_address  << adr
        self.tx.Write_Data     << data
        self.buff.reset()

    def request_data(self, adr, data):
        data.reset()
        self.buff.re_read()
        for asdadads in range(10):
            if self.buff.isReceivingData():
                self.buff >> self.c_data
                if self.c_data.address == adr:
                    data << self.c_data.data
                    return

        for asdas in range(3):
            if self.addr[asdas] == adr:
                return


        self.addr[2]  << adr
        self.data_requested << 1
        


class ram_block(v_entity):
    def __init__(self):
        super().__init__( )
        self.clk     =  port_in(v_sl())
        self.DataIO  =  port_Slave(ram_handler())
        
        self.architecture()
    
    @architecture
    def architecture(self):
        mem = v_signal( v_list(v_copy(self.DataIO.Write_Data),  10))
        @rising_edge(self.clk)
        def proc():
             

            if self.DataIO.write_enable:
                mem[self.DataIO.Write_address] << self.DataIO.Write_Data
        
            self.DataIO.read_data << mem[self.DataIO.read_address]

        end_architecture()

class ramHandler_tb(v_entity):
    def __init__(self):
        super().__init__()
        self.architecture()

    @architecture
    def architecture(self):
        clkgen = clk_generator()
        ram    = ram_block()
        ram.clk << clkgen.clk
        ram_master = ram_handle_master(ram.DataIO)
        data = v_slv(32)
        adr  = v_slv(32)
        
        data_out =  v_slv(32)
        addr_out  = v_slv(32)
        data_out_opt = optional_t(v_slv(32))

        @rising_edge(clkgen.clk)
        def proc():
            data << data + 10 
            adr << adr + 1
            if ram_master.ready_to_send() and adr < 10:
                ram_master.send_data(adr,data)

            if adr > 10:
                ram_master.request_data(addr_out, data_out)
                ram_master.request_data(addr_out, data_out_opt)
                if data_out_opt:
                    printf( str(value(addr_out)) +", " +str(value(data_out_opt.data)) + ", " + str(value(data_out)) +"\n" )
                    addr_out << addr_out + 1


            if addr_out > 8:
                addr_out << 0
            
        end_architecture()




@do_simulation
def RamHandler_sim(OutputPath, f= None):
    
    tb1 = ramHandler_tb()
    return tb1

@vhdl_conversion
def RamHandler_2vhdl(OutputPath, f= None):
    
    tb1 = ramHandler_tb()
    return tb1