from argg_hdl import *
from  argg_hdl.examples import *


#tb3 = InputDelay_tb()
#convert_to_hdl(tb3, "pyhdl_waveform")

class tb(v_entity):
    def __init__(self):
        super().__init__()
        self.architecture()

    @architecture
    def architecture(self):
        clkgen = v_create(clk_generator())
        data = v_slv(32,5)
        @rising_edge(clkgen.clk)
        def proc():
            data << data + 1
           

        end_architecture()


class small_buffer(v_class_master):
    def __init__(self,DataType= v_slv(32)):
        super().__init__()
        self.mem   = v_variable(v_list(v_copy(DataType),10))
        self.head  = v_variable(v_int())
        self.tail  = v_variable(v_int())
        self.count = v_variable(v_int())


    def isReceivingData(self):
        return self.count > 0
    
    def read_data(self, data):
        data << self.mem[self.tail]
        self.tail << self.tail + 1
        if self.tail > len(self.mem):
            self.tail << 0 

    def send_data(self, data):
        self.mem[self.head] << data 
        self.head << self.head + 1
        if self.head > len(self.mem):
            self.head << 0 



    def ready_to_send(self):
        return self.count < len(self.mem)


class ram_handler(v_class):
    def __init__(self, DataType = v_slv(32) , AddressType = v_slv(32)):
        super().__init__()
        self.write_enable  = port_out(v_sl())
        self.Write_address = port_out(AddressType)
        self.Write_Data    = port_out(DataType)
        
        self.read_address  = port_out(AddressType)
        self.read_data     = port_in(DataType)


class ram_block(v_entity):
    def __init__(self):
        super().__init__( )
        self.clk     =  port_in(v_sl())
        self.DataIO  =  port_Slave(ram_handler())
        
        self.architecture()
    
    @architecture
    def architecture(self):
        mem = v_signal( v_list(v_copy(self.DataIO.Write_Data),  10))
        s_mem = small_buffer()

        data_out = v_variable(self.DataIO.Write_Data)
        data_in = v_variable(self.DataIO.Write_Data)
        @rising_edge(self.clk)
        def proc():
            if s_mem.isReceivingData():
                s_mem.read_data(data_out)

            if s_mem.ready_to_send():
                s_mem.send_data(data_in)
                

            if self.DataIO.write_enable:
                mem[self.DataIO.Write_address] <= self.DataIO.Write_Data
        
            self.DataIO.read_data <= mem[self.DataIO.read_address]

        end_architecture()


tb1 = v_create(ram_block())

convert_to_hdl(tb1,"tests")