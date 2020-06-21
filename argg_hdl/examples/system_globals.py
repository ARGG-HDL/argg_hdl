


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
        


class system_globals(v_record):
    def __init__(self):
        super().__init__()
        self.clk   =  v_sl() 
        self.rst   =  v_sl() 
        self.reg   =  register_t() 

class system_globals_delay(v_entity):
    def __init__(self, gSystem, delay=5):
        super().__init__()
        self.gSystem     = port_in(gSystem)
        self.gSystem_out = port_out(gSystem)

    @architecture
    def architecture(self):
        
        self.gSystem_out.clk << self.gSystem.clk

        @rising_edge(self.gSystem.clk)
        def proc():
            self.gSystem_out.reg << self.gSystem.reg 
            self.gSystem_out.rst << self.gSystem.rst 
