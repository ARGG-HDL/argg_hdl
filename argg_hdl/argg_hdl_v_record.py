from argg_hdl.argg_hdl_base import *
from argg_hdl.argg_hdl_v_function import *
from argg_hdl.argg_hdl_v_entity_list import *

from argg_hdl.argg_hdl_v_class import v_class_converter,  v_class
from argg_hdl.argg_hdl_AST_MemFunctionCalls import memFunctionCall
from argg_hdl.argg_hdl_object_factory import add_constructor



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
    

        

class v_record(v_class):
    def __init__(self, Name=None, varSigConst=None):
        super().__init__(Name, varSigConst)
        self.__hdl_converter__ = v_record_converter()
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


def call_func_record_reset(obj, name, args, astParser=None,func_args=None):
    asOp = hdl.get_assiment_op(args[0])
    val = args[0].__hdl_converter__.get_init_values(args[0],args[0])
    
    ret =  str(args[0])  + asOp + val
    args[0]._add_output()
    return ret

class v_data_record(v_record):
    def __init__(self, Name=None, varSigConst=None):
        super().__init__(Name, varSigConst)
        self.__hdl_useDefault_value__ = False


add_constructor("v_data_record",v_data_record)
add_constructor("v_record",v_record)