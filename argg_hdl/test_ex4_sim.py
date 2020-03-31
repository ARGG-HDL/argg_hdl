

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
from argg_hdl.xgenPackage import *

def file_set_content(filename,content):
    with open(filename,'w') as f:
        f.write(content)

def file_get_contents(filename):
    with open(filename) as f:
        return f.read().strip()

ax = argg_hdl.example4.test_bench_e()
argg_hdl.example4.gsimulation.run_timed(ax, 1000,"example4.vcd")