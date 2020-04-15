
from argg_hdl import *

import argg_hdl.examples as  ahe

from .helpers import Folders_isSame, vhdl_conversion, do_simulation


@vhdl_conversion
def clk_generator_test(OutputFolder):

    clkgen = v_create(ahe.clk_generator())
    return clkgen
    
    




class tb_clk_generator(v_entity):
    def __init__(self,f):
        super().__init__()
        self.f = f
        self.architecture()

    @architecture
    def architecture(self):
        clkgen = v_create(ahe.clk_generator())
        
        data = v_slv(32,0)
      


        @rising_edge(clkgen.clk)
        def proc():
            data << data +1
            self.f.write(str(value(data)) +'\n')


@do_simulation
def clk_generator_test_sim(OutputFolder,f):

    tb = v_create(tb_clk_generator(f))
    return tb
    