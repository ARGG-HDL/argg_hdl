
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

def file_get_contents(filename):
    with open(filename) as f:
        return f.read().strip()

def file_set_content(filename,content):
    with open(filename,'w') as f:
        f.write(content)

class example1_test(unittest.TestCase):

    def test_Simulation(self):
        argg_hdl.Example1.gsimulation.reset()
        ax = argg_hdl.Example1.tb_entity()
        argg_hdl.Example1.gsimulation.run_timed(ax, 1000,"example1.vcd")
        print("===== end of Simulation =============")

        vcd = file_get_contents("example1.vcd")
        vcd_ref = file_get_contents("argg_hdl/tests/example1.vcd")
        self.assertTrue(vcd == vcd_ref)

    def test_Conversion(self):
        ax = argg_hdl.Example1.tb_entity()
        vhdl = ax._get_definition()
        file_set_content("argg_hdl/tests/example1_new.vhd",vhdl)
        vhdl_ref = file_get_contents("argg_hdl/tests/example1.vhd")
        self.assertTrue(vhdl == vhdl_ref)


class example2_test(unittest.TestCase):

    def test_Simulation(self):
        argg_hdl.example2.gsimulation.reset()
        ax = argg_hdl.example2.tb_entity()
        argg_hdl.example2.gsimulation.run_timed(ax, 1000,"example2.vcd")
        print("===== end of Simulation =============")

        vcd = file_get_contents("example2.vcd")
        vcd_ref = file_get_contents("argg_hdl/tests/example2.vcd")
        self.assertTrue(vcd == vcd_ref)

    def test_Conversion(self):
        
        ax = argg_hdl.example2.tb_entity()
      
        vhdl = ax._get_definition().strip() 
        
        file_set_content("argg_hdl/tests/example2_new.vhd",vhdl)
        vhdl_ref = file_get_contents("argg_hdl/tests/example2.vhd")
        self.assertTrue(vhdl == vhdl_ref)





class example3_test(unittest.TestCase):

    def test_Simulation(self):
        ax = argg_hdl.example3.tb_entity()
        argg_hdl.example3.gsimulation.run_timed(ax, 1000,"example3.vcd")
        print("===== end of Simulation =============")

        vcd = file_get_contents("example3.vcd")
        vcd_ref = file_get_contents("argg_hdl/tests/example3.vcd")
        self.assertTrue(vcd == vcd_ref)

    def test_Conversion(self):
        ax = argg_hdl.example3.tb_entity()
        vhdl = ax._get_definition().strip() 
        
        file_set_content("argg_hdl/tests/example3_new.vhd",vhdl)
        vhdl_ref = file_get_contents("argg_hdl/tests/example3.vhd")
        self.assertTrue(vhdl == vhdl_ref)


class example4_test(unittest.TestCase):

    def test_Simulation(self):
        argg_hdl.example4.gsimulation.reset()
        ax = argg_hdl.example4.tb_entity()
        argg_hdl.example4.gsimulation.run_timed(ax, 1000,"example4.vcd")
        print("===== end of Simulation =============")

        vcd = file_get_contents("example4.vcd")
        vcd_ref = file_get_contents("argg_hdl/tests/example4.vcd")
        self.assertTrue(vcd == vcd_ref)

    def test_Conversion(self):
        ax = argg_hdl.example4.tb_entity()
        vhdl = ax._get_definition().strip() 
        
        file_set_content("argg_hdl/tests/example4_new.vhd",vhdl)
        vhdl_ref = file_get_contents("argg_hdl/tests/example4.vhd")
        self.assertTrue(vhdl == vhdl_ref)
    
    def test_Conversion_filter(self):
        ax = argg_hdl.example4.axiFilter()
        vhdl = ax._get_definition().strip() 
        
        file_set_content("argg_hdl/tests/example4_filter_new.vhd",vhdl)
        vhdl_ref = file_get_contents("argg_hdl/tests/example4_filter.vhd")
        self.assertTrue(vhdl == vhdl_ref)


if __name__ == '__main__':
    unittest.main()



