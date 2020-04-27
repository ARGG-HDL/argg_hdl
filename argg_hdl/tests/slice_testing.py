from enum import Enum, auto

from argg_hdl import *
from  argg_hdl.examples import *

from .helpers import Folders_isSame, vhdl_conversion, do_simulation,printf




class slice_TB(v_entity):
    def __init__(self):
        super().__init__()
        self.architecture()


    @architecture
    def architecture(self):
        clkgen = v_create(clk_generator())
        counter = v_int()
        counter2 = v_int()
        counter3 = v_int(1)
        

        
        @rising_edge(clkgen.clk)
        def proc():
            counter << counter +1
            counter2[15:32] << counter[1:23]
            counter3[1:32] << counter3

         

            printf(repr(counter) + "; "+ repr(myState)+ "\n")
            


        end_architecture()


@do_simulation
def enum_TB_sim(OutputPath, f= None):
    
    tb1 = v_create(slice_TB())
    return tb1

@vhdl_conversion
def enum_TB_2vhdl(OutputPath, f= None):
    
    tb1 = v_create(slice_TB())
    return tb1