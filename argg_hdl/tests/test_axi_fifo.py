
from argg_hdl import *
from  argg_hdl.examples import *

from .helpers import Folders_isSame, vhdl_conversion, do_simulation,printf
from argg_hdl.argg_hdl_test_handler import add_test


class test_bench_axi_fifo(v_entity):
    def __init__(self):
        super().__init__()
        self.architecture()

    def architecture(self):
        clkgen = clk_generator()
        maxCount = v_slv(32,20)
        pipe1 = rollingCounter(clkgen.clk,maxCount) \
            | axiFifo(clkgen.clk)  \
            | axiFifo(clkgen.clk, depth = 5)  \
            | axiPrint(clkgen.clk) 
        
        end_architecture()






@do_simulation
def test_bench_axi_fifo_sim(OutputPath, f= None):
    tb = test_bench_axi_fifo()  
    return tb

def test_test_bench_axi_fifo_sim():
    return test_bench_axi_fifo_sim("tests/axi_fifo_sim/") 

add_test("axi_fifo_sim", test_test_bench_axi_fifo_sim)


@vhdl_conversion
def test_bench_axi_fifo_2vhdl(OutputPath, f= None):
    tb = test_bench_axi_fifo()  
    return tb


def test_test_bench_axi_fifo_2vhdl():
    return test_bench_axi_fifo_2vhdl("tests/axi_fifo/") 

add_test("axi_fifo_2vhdl", test_test_bench_axi_fifo_2vhdl)