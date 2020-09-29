from argg_hdl.argg_hdl_base import *
from argg_hdl.argg_hdl_v_function import *
from argg_hdl.argg_hdl_v_entity_list import *

import  argg_hdl.converter.vhdl_v_class_helpers as  vc_helper
import argg_hdl.argg_hdl_v_Package as argg_pack
from argg_hdl.argg_hdl_v_class import   v_class


class v_class_hanlde(v_class):
    def __init__(self,Name=None,varSigConst=None):
        super().__init__(Name,varSigConst)
        self.__hdl_converter__ =  get_primitive_hdl_converter("v_class_hanlde" )() 
        self.__vectorPush__   = True
        self.__vectorPull__   = True
        self._varSigConst       = varSig.combined_t


    def getType(self,Inout=None,varSigType=None):
        if self.__v_classType__ == v_classType_t.Record_t:
             return self._type 
        
        if Inout == InOut_t.input_t:
            return self.__hdl_converter__.get_NameSlave2Master(self)
        
        if Inout == InOut_t.output_t:
            return self.__hdl_converter__.get_NameMaster2Slave(self)
        
        if varSigType== varSig.signal_t:
            return self.__hdl_converter__.get_NameSignal(self) 
            
        return self._type 



