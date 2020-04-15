import unittest
import os
import shutil

from argg_hdl import *

import argg_hdl.examples as  ahe

import argg_hdl.tests.core_tests as core_t
import argg_hdl.tests.ex1 as ex1

class TestStringMethods(unittest.TestCase):

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


def remove_old_files():
    root, dirs, files = next(os.walk('tests/'))


    for d in dirs:
        path_output = os.path.join(root, d, "output")
        shutil.rmtree(path_output,ignore_errors=True)
        os.mkdir(path_output)

        path_temp = os.path.join(root, d, "temp")
        shutil.rmtree(path_temp,ignore_errors=True)
        os.mkdir(path_temp)

if __name__ == '__main__':
    remove_old_files()
    unittest.main()