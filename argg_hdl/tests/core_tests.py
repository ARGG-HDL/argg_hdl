
from argg_hdl import *

import argg_hdl.examples as  ahe

from .helpers import Folders_isSame, vhdl_conversion, do_simulation

from argg_hdl.argg_hdl_test_handler import add_test

@vhdl_conversion
def clk_generator_test(OutputFolder):

    clkgen = ahe.clk_generator()
    return clkgen
    
def test_clk_generator():
    return clk_generator_test("tests/example1/")
    

add_test("clk_generator", test_clk_generator)




class tb_clk_generator(v_entity):


    def __init__(self,f):
        super().__init__()
        self.f = f
        self.architecture()

    @architecture
    def architecture(self):
        clkgen = ahe.clk_generator()
        
        data = v_slv(32,0)
      


        @rising_edge(clkgen.clk)
        def proc():
            data << data +1
            self.f.write(str(value(data)) +'\n')


@do_simulation
def clk_generator_test_sim(OutputFolder,f):

    tb = tb_clk_generator(f)
    return tb

def test_clk_generator_sim():
    return clk_generator_test_sim("tests/example2/") 
    

add_test("clk_generator_sim", test_clk_generator_sim)