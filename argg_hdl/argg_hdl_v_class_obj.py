from argg_hdl.argg_hdl_base import *
from argg_hdl.argg_hdl_v_function import *
from argg_hdl.argg_hdl_v_entity_list import *
from argg_hdl.argg_hdl_simulation import *
import argg_hdl.argg_hdl_v_Package as argg_pack

from argg_hdl.argg_hdl_simulation import v_class_converter,  v_class

class v_class_obj_converter(v_class_converter):
    def __init__(self):
        super().__init__()

class v_class_obj(v_class):
    def __init__(self):
        super().__init__()

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