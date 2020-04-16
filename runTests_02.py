import unittest
import os
import shutil

from argg_hdl import *

import argg_hdl.examples as  ahe

from argg_hdl.tests.helpers  import remove_old_files

import argg_hdl.tests.core_tests as core_t
import argg_hdl.tests.ex1 as ex1
import argg_hdl.tests.RamHandler as RamHandler



class TestStringMethods(unittest.TestCase):
    def test_RamHandler_sim(self):
        result, message = RamHandler.RamHandler_sim("tests/RamHandler_sim/")
        self.assertTrue(result,message)
        

    def test_RamHandler2VHDL(self):
        result, message = RamHandler.RamHandler_2vhdl("tests/RamHandler/")
        self.assertTrue(result,message)
    

    

if __name__ == '__main__':
    remove_old_files()
    unittest.main()