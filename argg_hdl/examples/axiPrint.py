
import unittest
import functools
import argparse
import os,sys,inspect
import copy

from argg_hdl.argg_hdl_base import *
from argg_hdl.argg_hdl_v_symbol import *
from argg_hdl.examples.axiStream import *
from argg_hdl.argg_hdl_v_entity import *
from argg_hdl.argg_hdl_v_list import *

from argg_hdl.tests.helpers import *

class axiPrint(v_clk_entity):
    def __init__(self,clk=None):
        super().__init__(clk)
        self.Axi_in =  port_Stream_Slave(axisStream(v_slv(32)))
        self.architecture()

        
    def architecture(self):
        axiSalve =  get_salve(self.Axi_in)

        i_buff = v_slv(32)

        @rising_edge(self.clk)
        def proc():
            
            if axiSalve :
                i_buff << axiSalve
                printf("axiPrint valid: "+str(value(i_buff)) )
        
        end_architecture()