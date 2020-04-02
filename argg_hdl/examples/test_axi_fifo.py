

import unittest
import functools
import argparse
import os,sys,inspect
import copy
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 


from argg_hdl.argg_hdl_v_Package import *
from argg_hdl.argg_hdl_v_entity import *
from argg_hdl.rollingCounter import *
from argg_hdl.clk_generator import *
from argg_hdl.axiPrint import *
from argg_hdl.axi_fifo  import *

class test_bench_e123(v_entity):
    def __init__(self):
        super().__init__(__file__)
        self.architecture()

    def architecture(self):
        clkgen = v_create(clk_generator())
        maxCount = v_slv(32,20)
        pipe1 = rollingCounter(clkgen.clk,maxCount) \
            | axiFifo(clkgen.clk)  \
            | axiPrint(clkgen.clk) 
        
        end_architecture()

tb = test_bench_e123()

tb.hdl_conversion__.convert_all(tb,"test_fifo")


