import os,sys,inspect

from argg_hdl.argg_hdl_base import *
from argg_hdl.argg_hdl_v_symbol import v_symbol
from argg_hdl.argg_hdl__primitive_type_converter  import add_primitive_hdl_converter
from argg_hdl.argg_hdl_lib_enums import  *
from argg_hdl.converter.argg_hdl_hdl_converter_base import hdl_converter_base
from argg_hdl.argg_hdl_v_enum import  v_enum
from  argg_hdl.argg_hdl_object_name_maker import  make_object_name
import  argg_hdl.argg_hdl_hdl_converter as  hdl


class v_enum_converter(hdl_converter_base):
    def __init__(self):
        super().__init__()

    def get_type_simple(self,obj):
        
        objTypeName = obj.name        

        enumNames =[e.name for e in obj._type ] 
        ret = make_object_name(objTypeName,enumNames)
        return ret 


    def includes(self,obj, name,parent):
        PackageName = obj.__hdl_converter__.get_type_simple(obj)+"_pack"
        return "  use work." + PackageName+".all;\n"
    def def_packet_header(self,obj, name,parent):
        if  parent and parent._issubclass_("v_class"):
             return ""
            
        # type T_STATE is (RESET, START, EXECUTE, FINISH);
        name = hdl.get_type_simple(obj)
        enumNames =[e.name for e in obj._type ] 
        start = "" 
        ret =  "\n  type " + name + " is ( \n    " 
        for x in enumNames:
            ret += start + x
            start = ",\n    "
        ret += "\n  );\n\n"
        return ret
    
    def get_packet_file_name(self, obj):

        return obj.__hdl_converter__.get_type_simple(obj)+"_pack.vhd"

    def get_packet_file_content(self, obj):

        h1  = obj.__hdl_converter__.def_packet_header(obj,None,None)
        PackageName = obj.__hdl_converter__.get_type_simple(obj)+"_pack"
        fileContent = """
library IEEE;
library work;
use IEEE.numeric_std.all;
use IEEE.std_logic_1164.all;
use ieee.std_logic_unsigned.all;
use work.argg_hdl_core.all;

package {PackageName} is 
{pack}
end {PackageName};


package body {PackageName} is

end  {PackageName};

""".format(
    PackageName=PackageName,
    pack=h1
)

        


        return fileContent
    
    def def_recordMember(self, obj, name, parent,Inout=None):
        if parent._issubclass_("v_class"):
            if obj._Inout == InOut_t.Slave_t:
                Inout = InoutFlip(Inout)
            return name + " : " + hdl.get_type_simple(obj)
       
        return ""

    def def_def_record_Member_Default(self, obj, name, parent,Inout=None):
        if parent._issubclass_("v_class"):
            if obj._Inout == InOut_t.Slave_t:
                Inout = InoutFlip(Inout)

            return name + " => " + str(v_enum((obj._type(value(obj)))))

        return ""
    
    def get_process_header(self,obj):
        if obj._Inout != InOut_t.Internal_t:
            return ""
        
        if obj._varSigConst != varSig.variable_t:
            return ""

        VarSymb = get_varSig(obj._varSigConst)

        return VarSymb +" " +str(obj) + " : " +  hdl.get_type_simple(obj) +" := " + obj._type(value(obj.symbol)).name +";\n"

    
    def get_architecture_header(self, obj):
        if obj._Inout != InOut_t.Internal_t:
            return ""
        
        if obj._varSigConst != varSig.signal_t or obj._varSigConst != varSig.signal_t:
            return ""

        VarSymb = get_varSig(obj._varSigConst)

        return VarSymb +" " +str(obj) + " : " +  hdl.get_type_simple(obj) +" := " +obj._type(value(obj.symbol)).name+";\n"


add_primitive_hdl_converter("v_enum" ,v_enum_converter)
