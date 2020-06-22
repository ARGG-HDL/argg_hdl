


from argg_hdl.argg_hdl_base import *
from argg_hdl.argg_hdl_v_symbol import *

from argg_hdl.argg_hdl_simulation import *
from argg_hdl.argg_hdl_v_entity import *
from argg_hdl.argg_hdl_v_class import *
from argg_hdl.argg_hdl_v_record import *


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
    def __init__(self, gSystem):
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