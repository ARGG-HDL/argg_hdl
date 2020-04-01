

import unittest
import functools
import argparse
import os,sys,inspect
import copy
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

import argg_hdl.Example1 
import argg_hdl.example2 
import argg_hdl.example3 
import argg_hdl.example4 
from argg_hdl.argg_hdl_v_Package import *

def file_set_content(filename,content):
    with open(filename,'w') as f:
        f.write(content)

def file_get_contents(filename):
    with open(filename) as f:
        return f.read().strip()


#ax = argg_hdl.example4.tb_entity()
#vhdl = ax.hdl_conversion__.get_entity_definition(ax)
#file_set_content("argg_hdl/tests/example1_new.vhd",vhdl)
#vhdl_ref = file_get_contents("argg_hdl/tests/example1.vhd")
#print(vhdl == vhdl_ref)
#print(vhdl)

tb = argg_hdl.example4.test_bench_e()

tb.hdl_conversion__.convert_all(tb,"asdadasd")


