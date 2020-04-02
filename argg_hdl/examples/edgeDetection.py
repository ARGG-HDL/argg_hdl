import argparse
import os,sys,inspect


from argg_hdl.argg_hdl_base import *
from argg_hdl.argg_hdl_v_Package import *
from argg_hdl.argg_hdl_v_class import *

from enum import Enum 
import copy 


class edgeDetection(v_class):
    def __init__(self):
        super().__init__("edgeDetection")
        self.rx = port_in (v_sl())
        self.__v_classType__         = v_classType_t.Slave_t
       
        self.oldRX =v_sl()
        self.oldRX1 =v_sl()

    def _onPull(self):
        self.oldRX1 << self.oldRX
        self.oldRX << self.rx
    
    def rising_edge(self):
        return not self.oldRX1 and self.oldRX

    def falling_edge(self):
        return  self.oldRX1 and not self.oldRX

        

