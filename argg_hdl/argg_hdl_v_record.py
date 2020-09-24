from argg_hdl.argg_hdl_base import *
from argg_hdl.argg_hdl_v_function import *
from argg_hdl.argg_hdl_v_entity_list import *

from argg_hdl.argg_hdl_v_class import   v_class
from argg_hdl.ast.argg_hdl_AST_MemFunctionCalls import memFunctionCall
from argg_hdl.argg_hdl_object_factory import add_constructor



    

        

class v_record(v_class):
    def __init__(self, Name=None, varSigConst=None):
        super().__init__(Name, varSigConst)
        self.__hdl_converter__ = get_primitive_hdl_converter("v_record" )() 
        self.__v_classType__ = v_classType_t.Record_t
        self.__hdl_converter__.append_reset(self)
        #self.__hdl_useDefault_value__ = False
 

    def reset(self):
        mem = self.getMember()
        for x in mem:
            x["symbol"].reset()

    def getType(self, Inout=None, varSigType=None):
        return self._type

    def get_vhdl_name(self, Inout=None):
        return str(self.__hdl_name__)

    def getTypes(self):
        return {
            "main" : self._type
        }

    def setInout(self, Inout):
        if self._Inout == Inout:
            return

        if Inout == InOut_t.Master_t:
            self._Inout = InOut_t.output_t
        elif Inout == InOut_t.Slave_t:
            self._Inout = InOut_t.input_t
        else:
            self._Inout = Inout

        if Inout == InOut_t.Internal_t:
            Inout = InOut_t.Master_t
        members = self.getMember()
        for x in members:
            x["symbol"].setInout(Inout)




class v_data_record(v_record):
    def __init__(self, Name=None, varSigConst=None):
        super().__init__(Name, varSigConst)
        self.__hdl_useDefault_value__ = False


add_constructor("v_data_record",v_data_record)
add_constructor("v_record",v_record)