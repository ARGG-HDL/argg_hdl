


from argg_hdl.argg_hdl_base import *
from argg_hdl.argg_hdl_v_symbol import *

from argg_hdl.argg_hdl_simulation import *
from argg_hdl.argg_hdl_v_entity import *
from argg_hdl.argg_hdl_v_class import *
from argg_hdl.argg_hdl_v_record import *
from argg_hdl.argg_hdl_v_list import *
from argg_hdl.argg_hdl_master_slave import *


class register_t(v_record):
    def __init__(self):
        super().__init__()
        self.address   = v_slv(16) 
        self.value     = v_slv(16) 
    
    def get_value(self, addr, data):
        if self.address == addr: 
            self.value >> data



class system_globals(v_record):
    def __init__(self):
        super().__init__()
        self.clk   =  v_sl() 
        self.rst   =  v_sl() 
        self.reg   =  register_t() 



class system_globals_delay(v_entity):
    def __init__(self, gSystem=system_globals()):
        super().__init__()
        self.gSystem      = port_in(gSystem)
        self.gSystem      << gSystem
        self.register_out = port_out(register_t())
        self.architecture()

    @architecture
    def architecture(self):

        reg_out1 =v_signal(register_t())
        reg_out2 = v_signal(register_t())
        reg_out3 = v_signal(register_t())
        reg_out4 =v_signal( register_t())

        @rising_edge(self.gSystem.clk)
        def proc():
            reg_out1      << self.gSystem.reg 
            reg_out2      << reg_out1
            reg_out3      << reg_out2
            reg_out4      << reg_out3
            self.register_out  << reg_out4

        end_architecture()


class register_handler(v_class_master):
    def __init__(self,gSystem = system_globals()):
        super().__init__()
        self.__hdl_useDefault_value__ = False
        self.gSystem  = signal_port_Slave(gSystem)
        self.gSystem  << gSystem
        self.localStorage = v_list( register_t() , 0 , varSig.signal_t)
        self.architecture()    

    def get_register(self, RegisterAddres):
        reg =  register_t()
        reg.address << RegisterAddres
        self.localStorage.append(reg)
        return reg.value




    @architecture
    def architecture(self):

        registers = system_globals_delay(self.gSystem)

        @rising_edge(self.gSystem.clk)
        def proc_register_handler():
            for ele in  self.localStorage:
                if registers.register_out.address == ele.address:
                    ele.value << registers.register_out.value

        end_architecture()