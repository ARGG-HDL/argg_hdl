import unittest
import os
import shutil

from argg_hdl import *

import argg_hdl.examples as  ahe

from argg_hdl.tests.helpers  import remove_old_files

import argg_hdl.tests.core_tests as core_t
import argg_hdl.tests.ex1 as ex1
import argg_hdl.tests.RamHandler as RamHandler
import argg_hdl.tests.test_axi_fifo as test_axi_fifo
import argg_hdl.tests.Signal_Variable_class as Signal_Variable_class
import argg_hdl.tests.Native_fifo as Native_fifo
import argg_hdl.tests.EnumTest as EnumTest

class TestCoreExamples(unittest.TestCase):

    def test_clk_generator(self):
        result, message = core_t.clk_generator_test("tests/example1/")
        self.assertTrue(result,message)
        

    def test_clk_generator_sim(self):
        result, message = core_t.clk_generator_test_sim("tests/example2/")
        self.assertTrue(result,message)

    def test_InputDelay_sim(self):
        result, message = ex1.InputDelay_sim("tests/ex1/")
        self.assertTrue(result,message)

    def test_InputDelay2vhdl(self):
        result, message = ex1.InputDelay2vhdl("tests/ex1_vhdl/")
        self.assertTrue(result,message)

    def test_RamHandler_sim(self):
        result, message = RamHandler.RamHandler_sim("tests/RamHandler_sim/")
        self.assertTrue(result,message)
        

    def test_RamHandler2VHDL(self):
        result, message = RamHandler.RamHandler_2vhdl("tests/RamHandler/")
        self.assertTrue(result,message)



    def test_axi_fifo_sim(self):
        result, message = test_axi_fifo.test_bench_axi_fifo_sim("tests/axi_fifo_sim/")
        self.assertTrue(result,message)
    
    def test_axi_fifo_2vhdl(self):
        result, message = test_axi_fifo.test_bench_axi_fifo_2vhdl("tests/axi_fifo/")
        self.assertTrue(result,message)      

    def var_sig_tb_2vhdl(self):
        result, message = Signal_Variable_class.var_sig_tb_2vhdl("tests/var_sig_class")
        self.assertTrue(result,message)       


    def var_sig_tb_sim(self):
        result, message = Signal_Variable_class.var_sig_tb_sim("tests/var_sig_class_sim")
        self.assertTrue(result,message)     


    def test_native_fifo_sim(self):
        result, message =  Native_fifo.fifo_cc_tb_sim("tests/native_fifo_sim")
        self.assertTrue(result,message)       


    def test_native_fifo_2vhdl(self):
        result, message = Native_fifo.fifo_cc_tb_2vhdl("tests/native_fifo")
        self.assertTrue(result,message)     


    def test_enums_sim(self):
        result, message =  EnumTest.enum_TB_sim("tests/enumTest_sim")
        self.assertTrue(result,message)       


    def test_enums_2vhdl(self):
        result, message = EnumTest.enum_TB_2vhdl("tests/enumTest")
        self.assertTrue(result,message)     

        
if __name__ == '__main__':
    remove_old_files()
    unittest.main()