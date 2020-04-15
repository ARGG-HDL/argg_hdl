from argg_hdl import *
from  argg_hdl.examples import *


#tb3 = InputDelay_tb()
#convert_to_hdl(tb3, "pyhdl_waveform")





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
        data.reset()

        if self.count > 0:
            data << self.mem[self.tail]
            self.tail << self.tail + 1
            self.count << self.count - 1
        

        if self.tail > len(self.mem) - 1:
            self.tail << 0 

    def __rshift__(self, rhs):
        rhs.reset()

        if self.count > 0:
            rhs << self.mem[self.tail]
            self.tail << self.tail + 1
            self.count << self.count - 1
        

        if self.tail > len(self.mem) - 1:
            self.tail << 0 

    def send_data(self, data):
        if self.ready_to_send():
            self.mem[self.head] << data 
            self.head << self.head + 1
            self.count << self.count + 1
            if self.head > len(self.mem) - 1:
                self.head << 0 
                
    def __lshift__(self,rhs):
        if self.ready_to_send():
            self.mem[self.head] << rhs 
            self.head << self.head + 1
            self.count << self.count + 1
            if self.head > len(self.mem) - 1:
                self.head << 0 

    def length(self):
        return len(self.mem)

    def ready_to_send(self):
        return self.count < len(self.mem)

    def __len__(self):
        return len(self.mem)

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
        @rising_edge(self.clk)
        def proc():
             

            if self.DataIO.write_enable:
                mem[self.DataIO.Write_address] <= self.DataIO.Write_Data
        
            self.DataIO.read_data << mem[self.DataIO.read_address]

        end_architecture()

class tb(v_entity):
    def __init__(self):
        super().__init__()
        self.architecture()

    @architecture
    def architecture(self):
        clkgen = v_create(clk_generator())
        ram    = v_create(ram_block())
        ram.clk << clkgen.clk

        data = v_slv(32,1000)
        adsdata = v_slv(32,1000)
        m_counter  = v_slv(32,5)
        s_counter =  v_variable( v_slv(32,5))
        s_mem = small_buffer()
        opt_data = optional_t()
        @rising_edge(clkgen.clk)
        def proc():
            m_counter << m_counter + 1 
            m_counter >> s_counter
            if m_counter > 15 and s_mem:
                data << data + 1
                s_mem.send_data(data)
                s_mem << data
            
            opt_data << m_counter
            if m_counter > 20:
                m_counter << 0
                for index in range( len(s_mem) ):
                    s_mem.read_data(opt_data)
                    s_mem >> opt_data
                    if opt_data:
                    
                        opt_data.get_data(adsdata)
                        s_counter << s_counter + 1
           

        end_architecture()



#run_simulation(tb1, 30000,"ram_tb.vcd")
#convert_to_hdl(tb1,"tests")

@vhdl_conversion
def ex2_2vhdl(OutputPath):
    
    tb1 = v_create(tb())
    return tb1