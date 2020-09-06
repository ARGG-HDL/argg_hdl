
from argg_hdl import *
from  argg_hdl.examples import *

from .helpers import Folders_isSame, vhdl_conversion, do_simulation,printf

class sin_composer(v_entity):
    def __init__(self):
        super().__init__( )
        self.clk     =  port_in(v_sl())
        
        self.architecture()
    
    @architecture
    def architecture(self):
        