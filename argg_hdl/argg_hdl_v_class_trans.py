from argg_hdl.argg_hdl_base import *
from argg_hdl.argg_hdl_v_function import *
from argg_hdl.argg_hdl_v_entity_list import *
from argg_hdl.argg_hdl_simulation import *
import argg_hdl.argg_hdl_v_Package as argg_pack

from argg_hdl.argg_hdl_v_class import v_class_converter,  v_class, append_hdl_name

class v_class_trans_converter(v_class_converter):
    def __init__(self):
        super().__init__()

    def _vhdl__reasign(self, obj, rhs, astParser=None,context_str=None):
        
        asOp = obj.__hdl_converter__.get_assiment_op(obj)

        
        if rhs._Inout == InOut_t.Master_t:
            raise Exception("cannot read from Master")
        if rhs._Inout == InOut_t.output_t:
            raise Exception("cannot read from Output")


        
        if rhs._type != obj._type:
            raise Exception("cannot assigne different types.", str(obj), rhs._type, obj._type )
        
        ret ="---------------------------------------------------------------------\n--  " + obj.get_vhdl_name() +" << " + rhs.get_vhdl_name()+"\n" 
        ret += obj.get_vhdl_name(InOut_t.output_t) + asOp + rhs.get_vhdl_name(InOut_t.output_t) +";\n" 
        ret += rhs.get_vhdl_name(InOut_t.input_t) + asOp + obj.get_vhdl_name(InOut_t.input_t)
        return ret 

    def _vhdl__reasign_rshift_(self, obj, rhs, astParser=None,context_str=None):
        raise Exception("Unsupported r shift", str(obj), rhs._type, obj._type )        

    def _vhdl_get_attribute(self,obj, attName):
        attName = str(attName)
        if obj._varSigConst != varSig.variable_t:
            for x in obj.getMember():
                if x["name"] == attName:

                    if x["symbol"]._Inout  == InOut_t.output_t:
                        suffix = "_m2s"
                    else:
                        suffix = "_s2m"

                    return obj.get_vhdl_name() + suffix + "." +   attName
        
          
        return obj.get_vhdl_name() + "." +str(attName)


    def make_connection(self, obj, name, parent):
        obj.pull          =  obj.__hdl_converter__.getConnecting_procedure(obj, InOut_t.input_t , "pull", procedureName="pull" )
        obj.push          =  obj.__hdl_converter__.getConnecting_procedure(obj, InOut_t.output_t, "push", procedureName="push")
        obj.pull_rev      =  obj.__hdl_converter__.getConnecting_procedure(obj, InOut_t.output_t, "pull", procedureName="pull")
        obj.push_rev      =  obj.__hdl_converter__.getConnecting_procedure(obj, InOut_t.input_t , "push", procedureName="push")
            
        

class v_class_trans(v_class):
    def __init__(self,Name=None,varSigConst=None):
        super().__init__(Name,varSigConst)
        self.__hdl_converter__ = v_class_trans_converter()
        self.__v_classType__ = v_classType_t.transition_t 

    def get_vhdl_name(self,Inout=None):
        if Inout is None:
            return str(self.__hdl_name__)
        

        if Inout== InOut_t.input_t:
            return append_hdl_name(str(self.__hdl_name__), "_s2m")
        
        if Inout== InOut_t.output_t:
            return append_hdl_name(str(self.__hdl_name__), "_m2s")
        
        return None    