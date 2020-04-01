
import unittest
import functools
import argparse
import os,sys,inspect
import copy

from .argg_hdl_base import *
from .argg_hdl_v_symbol import *
from .argg_hdl_v_entity import *
from .argg_hdl_v_list import *




class clk_generator(v_entity):
    def __init__(self):
        super().__init__(__file__)
        self.clk = port_out(v_sl())
        self.architecture()
    
    @architecture
    def architecture(self):
        
        @timed()
        def proc():
            self.clk << 1
            #print("======================")
            yield wait_for(10)
            self.clk << 0
            yield wait_for(10)

