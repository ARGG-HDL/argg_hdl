from argg_hdl.argg_hdl_base import *
from argg_hdl.argg_hdl_v_function import *
from argg_hdl.argg_hdl_v_entity_list import *
from argg_hdl.converter.argg_hdl_v_class_converter import v_class_converter
from argg_hdl.argg_hdl_v_class import   v_class
from argg_hdl.ast.argg_hdl_AST_MemFunctionCalls import memFunctionCall
from argg_hdl.argg_hdl_object_factory import add_constructor

from argg_hdl.argg_hdl__primitive_type_converter  import add_primitive_hdl_converter

class v_record_converter(v_class_converter):
    def __init__(self):
        super().__init__()
        self.functionNameVetoList.append("reset")



    def append_reset(self, obj):
        self.MemfunctionCalls.append(
        memFunctionCall(
            name= "reset",
            args=  [obj],
            obj= obj,
            call_func = call_func_record_reset,
            func_args = None,
            setDefault = False,
            varSigIndependent = True
        )
     )


    def make_connection(self, obj, name, parent):
        obj.pull = self.getConnecting_procedure_record(obj, "pull")
        obj.push = self.getConnecting_procedure_record(obj, "push")

    def getConnecting_procedure_record(self, obj, PushPull):

        if PushPull == "push":
            inout = " out "
            line = "data_IO  <=  self;"
        else:
            inout = " in "
            line = "self  := data_IO;"

        TypeName = obj.getType()
        args = "self : inout " + TypeName + "; signal data_IO : " + inout + " " + TypeName

        ret = v_procedure(
            name=None,
            argumentList=args,
            body=line,
            isFreeFunction=True,
            IsEmpty=False
        )

        return ret

    def _vhdl_get_attribute(self,obj, attName):
        return obj.get_vhdl_name() + "." +str(attName)
    
    def _vhdl__reasign(self, obj, rhs, astParser=None,context_str=None):

        if rhs._Inout == InOut_t.Master_t:
            raise Exception("cannot read from Master")

        if rhs._Inout == InOut_t.output_t:
            raise Exception("cannot read from Output")
            
        if rhs._type != obj._type:
            raise Exception("cannot assigne different types.", str(obj), rhs._type, obj._type )

        asOp = hdl.get_assiment_op(obj)
        obj._add_output()
        return obj.get_vhdl_name() + asOp +  rhs.get_vhdl_name()
    
    def _vhdl__reasign_rshift_(self, obj, rhs, astParser=None,context_str=None):
        return hdl._vhdl__reasign(rhs,obj,astParser,context_str)
    
def call_func_record_reset(obj, name, args, astParser=None,func_args=None):
    asOp = hdl.get_assiment_op(args[0])
    val = args[0].__hdl_converter__.get_init_values(args[0],args[0])
    
    ret =  str(args[0])  + asOp + val
    args[0]._add_output()
    return ret

add_primitive_hdl_converter("v_record",v_record_converter )