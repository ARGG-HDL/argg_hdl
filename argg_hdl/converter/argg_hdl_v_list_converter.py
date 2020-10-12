import os
import sys
import inspect
from typing import TypeVar, Generic


from argg_hdl.argg_hdl__primitive_type_converter  import add_primitive_hdl_converter
from argg_hdl.argg_hdl_base import *
from argg_hdl.argg_hdl_v_symbol import *
from argg_hdl.argg_hdl_v_list import *
from argg_hdl.converter.argg_hdl_hdl_converter_base import hdl_converter_base
    
    
class v_list_converter(hdl_converter_base):
    def __init__(self):
        super().__init__()
        self.obj_list = []
    def includes(self,obj, name,parent):
        ret  = """
library IEEE;
use IEEE.numeric_std.all;
use IEEE.std_logic_1164.all;
use ieee.std_logic_unsigned.all;
        """

        ret += obj.Internal_Type.__hdl_converter__.includes(obj.Internal_Type,name,obj)
        return ret




    def get_get_call_member_function(self, obj, name, args):
        ret = None
        args = [x.get_symbol() for x in args ]
        if name =="reset":
            ret = memFunctionCall(
            name= name,
            args= args,
            obj= obj,
            call_func = call_func_v_list_reset,
            func_args = None,
            setDefault = False,
            varSigIndependent = True
        )
        return ret
 

    def def_entity_port(self,obj):
        ret = []
        obj.Internal_Type._Inout = obj._Inout
        xs = obj.Internal_Type.__hdl_converter__.extract_conversion_types(obj.Internal_Type)

        for x in xs:
            if x["symbol"].__v_classType__ ==  v_classType_t.transition_t:
                continue
            inoutstr = " : "+ x["symbol"].__hdl_converter__.InOut_t2str(x["symbol"]) +" "
            ret.append( obj.get_vhdl_name() +x["suffix"] + inoutstr +x["symbol"]._type + "_a(0 to "+ str(obj.size)   +") := (others => " + x["symbol"]._type + "_null)")
    
        return ret

    def InOut_t2str(self, obj):
        inOut = obj._Inout
        if inOut == InOut_t.input_t:
            return " in "
        
        if inOut == InOut_t.output_t:
            return " out "
        
        if inOut == InOut_t.InOut_tt:
            return " inout "
        
        inOut = obj.__writeRead__
        if inOut == InOut_t.input_t:
            return " in "
        
        if inOut == InOut_t.output_t:
            return " out "
        
        if inOut == InOut_t.InOut_tt:
            return " inout "
        
        for x in obj.__hdl_converter__.obj_list:
            try:
                ret = x.__hdl_converter__.InOut_t2str(x)
                return ret
            except:
                pass


        raise Exception("unkown Inout type",inOut)

    def impl_entity_port(self, obj, name):
        ret = []
        obj.Internal_Type.set_vhdl_name(obj.__hdl_name__, True)

        xs =obj.Internal_Type.__hdl_converter__.extract_conversion_types(obj.Internal_Type, 
                exclude_class_type= v_classType_t.transition_t
            )
        for x in xs:
            ret.append( name + x["suffix"] + " => " + x["symbol"].get_vhdl_name())

        return ret

    def impl_architecture_header(self, obj):
        ret =""

        obj1 =obj.Internal_Type.__hdl_converter__.extract_conversion_types(obj.Internal_Type)
        
        for x in obj1:
            if x["symbol"]._issubclass_("v_class") and x["symbol"].__v_classType__ ==  v_classType_t.transition_t:
                continue
            if x["symbol"]._varSigConst == varSig.variable_t:
                continue
            if obj._Inout != InOut_t.Internal_t and not obj.__isInst__:
                continue

            ret += """  {VarSymb} {objName} : {objType}(0 to {size} - 1)  := (others => {defaults});\n""".format(
                VarSymb=get_varSig(x["symbol"]._varSigConst),
                objName=obj.get_vhdl_name(x["symbol"]._Inout),
                objType=x["symbol"].__hdl_converter__.get_Name_array(x["symbol"]),
                defaults=x["symbol"].__hdl_converter__.get_default_value(x["symbol"]),
                size = obj.size
            )
        return ret

    def def_packet_header(self,obj, name,parent):
        return "-- v_list getHeader\n"    
    
    def def_record_Member(self,obj, name,parent,Inout=None):
        ret =""

        obj1 =obj.Internal_Type.__hdl_converter__.extract_conversion_types(obj.Internal_Type)
        for x in obj1:

            ret += """{objName} : {objType}(0 to {size} - 1 )""".format(
                objName=name,
                objType=x["symbol"].__hdl_converter__.get_Name_array(x["symbol"]),
                size = obj.size
            )
        return ret
    
    def def_record_Member_Default(self, obj, name,parent,Inout=None):
        ret =""

        obj1 =obj.Internal_Type.__hdl_converter__.extract_conversion_types(obj.Internal_Type)
        for x in obj1:

            ret += """{objName} => (others => {defaults})""".format(
                objName=name,
                defaults=x["symbol"].__hdl_converter__.get_default_value(x["symbol"]),
                size = obj.size
            )
        return ret
        
    
    def impl_slice(self,obj, sl,astParser=None):
        if issubclass(type(sl),argg_hdl_base0):
            sl = sl.__hdl_converter__.impl_get_value(sl,ReturnToObj=v_int(),astParser=astParser)
        
        ret = v_copy(obj.Internal_Type)
        ret._varSigConst = obj._varSigConst
      
        if type(sl).__name__ == "v_slice":
            sl.set_source(obj)
            sl.reversed = True
            
        ret.__hdl_name__ =  obj.__hdl_name__+"("+str(sl)+")"
        
        self.obj_list.append(ret)

        return ret
    def get_process_header(self,obj):
        ret =""

        obj1 =obj.Internal_Type.__hdl_converter__.extract_conversion_types(obj.Internal_Type)
        
        for x in obj1:
            if x["symbol"]._varSigConst != varSig.variable_t:
                continue

            ret += """  {VarSymb} {objName} : {objType}(0 to {size} - 1)  := (others => {defaults});\n""".format(
                VarSymb=get_varSig(x["symbol"]._varSigConst),
                objName=obj.get_vhdl_name(x["symbol"]._Inout),
                objType=x["symbol"].__hdl_converter__.get_Name_array(x["symbol"]),
                defaults=x["symbol"].__hdl_converter__.get_default_value(x["symbol"]),
                size = obj.size
            )
        return ret
        
    def to_arglist(self,obj, name,parent,withDefault = False,astParser=None):
        return name +" : " + obj.__hdl_converter__.InOut_t2str(obj)+"  " +obj.get_type()

    def impl_reasign(self, obj:"v_symbol", rhs, astParser=None,context_str=None):
    #def impl_reasign(self, obj, rhs, context=None):
        asOp = obj.__hdl_converter__.get_assiment_op(obj)
        return str(obj.__hdl_name__) + asOp +  str(rhs.__hdl_name__)

    def _vhdl__Pull(self,obj):
        ret = ""
        if obj.driver is None:
            return ret

        if obj.Internal_Type.__vectorPull__:
            driver_name  = str(obj.driver)
            if obj.Internal_Type.__v_classType__ == v_classType_t.Master_t:
                driver_name =  str(obj.driver) +"_s2m"
            elif obj.Internal_Type.__v_classType__ == v_classType_t.Slave_t:
                driver_name = str(obj.driver) +"_m2s"

            ret += "  pull(" + str(obj) +", "+ driver_name +");\n  "
            return ret


        raise Exception("Not implemented")

    def _vhdl__push(self,obj):
        ret = ""
        if obj.driver is None:
            return ret

        if obj.Internal_Type.__vectorPush__:
            driver_name  = str(obj.driver)
            if obj.Internal_Type.__v_classType__ == v_classType_t.Master_t:
                driver_name = str(obj.driver) +"_m2s"
            elif obj.Internal_Type.__v_classType__ == v_classType_t.Slave_t:
                driver_name =  str(obj.driver) +"_s2m"

            ret += "  push(" + str(obj) +", "+ driver_name +");\n  "
            return ret


        raise Exception("Not implemented")

    def length(self,obj):
        ret = v_int()
        ret.__hdl_name__=str(obj)+"'length"
        return ret  

add_primitive_hdl_converter("v_list",v_list_converter )
