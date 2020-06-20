from enum import Enum, auto

from argg_hdl import *
from  argg_hdl.examples import *

from .helpers import Folders_isSame, vhdl_conversion, do_simulation,printf



class myStates(Enum):
    e_idle = auto()
    e_running_1 =  auto()
    e_running_2 = auto()
    some_other_state =  auto()
    some_other_state2 =  auto()



class enum_TB(v_entity):
    def __init__(self):
        super().__init__()
        self.architecture()


    @architecture
    def architecture(self):
        clkgen = clk_generator()
        counter = v_int()
        myState = v_enum( myStates.e_idle)
        myState2 = v_enum( myStates.e_idle)

        
        @rising_edge(clkgen.clk)
        def proc():
            counter << counter +1

            if counter == 10:
                myState << myStates.e_running_1

            if counter == 20:
                myState << myStates.e_running_2
            
            if counter == 30:
                myState << myStates.some_other_state
            
            
            if counter == 40:
                myState << myStates.some_other_state2
            
            if counter == 50:
                counter << 0
                myState << myState2

            printf(repr(counter) + "; "+ repr(myState)+ "\n")
            


        end_architecture()


@do_simulation
def enum_TB_sim(OutputPath, f= None):
    
    tb1 = enum_TB()
    return tb1

@vhdl_conversion
def enum_TB_2vhdl(OutputPath, f= None):
    
    tb1 = enum_TB()
    return tb1