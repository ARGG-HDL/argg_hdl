import os
import sys
import inspect
from typing import TypeVar, Generic

from argg_hdl.argg_hdl_base import *
from argg_hdl.argg_hdl_v_symbol import *

    
    
class v_list_converter(hdl_converter_base):
    def __init__(self):
        super().__init__()
        self.obj_list = []
    def includes(self,obj, name,parent):
        ret  = """
library IEEE;
library UNISIM;
use IEEE.numeric_std.all;
use IEEE.std_logic_1164.all;
use UNISIM.VComponents.all;
use ieee.std_logic_unsigned.all;
        """
        if "std_logic_vector"  in obj.Internal_Type._type:
            ret +=  "  use work."+obj._type+"_pack.all;\n"

        ret += obj.Internal_Type.__hdl_converter__.includes(obj.Internal_Type,name,obj)
        return ret


    def get_packet_file_name(self, obj):
        if "std_logic_vector" not in obj.Internal_Type._type:
            return ""
        return obj._type+"_pack.vhd"

    def get_packet_file_content(self, obj):

        if "std_logic_vector" not in obj.Internal_Type._type:
            return ""

        includes = obj.__hdl_converter__.includes(obj,None,None)
        includes = make_unique_includes(includes, obj._type+"_pack")
        ret =  """ 
-- XGEN: Autogenerated File

{includes}


package {objType}_pack is 
  type {objType} is array (natural range <>) of {Internal_Type};
end {objType}_pack;

package body {objType}_pack is

end {objType}_pack;
""".format(
    objType=obj._type,
    size = obj.get_size(),
    Internal_Type=obj.Internal_Type._type,
    includes=includes
)
        return ret

    def get_port_list(self,obj):
        ret = []
        obj.Internal_Type._Inout = obj._Inout
        xs = obj.Internal_Type.__hdl_converter__.extract_conversion_types(obj.Internal_Type)

        for x in xs:
            if x["symbol"].__v_classType__ ==  v_classType_t.transition_t:
                continue
            inoutstr = " : "+ x["symbol"].__hdl_converter__.InOut_t2str(x["symbol"]) +" "
            ret.append( obj.get_vhdl_name() +x["suffix"] + inoutstr +x["symbol"]._type + "_a("+ str(obj.size)   +" downto 0) := (others => " + x["symbol"]._type + "_null)")
    
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

    def _vhdl_make_port(self, obj, name):
        ret = []
        obj.Internal_Type.set_vhdl_name(obj.__hdl_name__, True)

        xs =obj.Internal_Type.__hdl_converter__.extract_conversion_types(obj.Internal_Type, 
                exclude_class_type= v_classType_t.transition_t
            )
        for x in xs:
            ret.append( name + x["suffix"] + " => " + x["symbol"].get_vhdl_name())

        return ret

    def get_architecture_header(self, obj):
        ret =""

        obj1 =obj.Internal_Type.__hdl_converter__.extract_conversion_types(obj.Internal_Type)
        
        for x in obj1:
            if x["symbol"]._issubclass_("v_class") and x["symbol"].__v_classType__ ==  v_classType_t.transition_t:
                continue
            if x["symbol"]._varSigConst == varSig.variable_t:
                continue
            if obj._Inout != InOut_t.Internal_t and not obj.__isInst__:
                continue

            ret += """  {VarSymb} {objName} : {objType}({size} - 1 downto 0)  := (others => {defaults});\n""".format(
                VarSymb=get_varSig(x["symbol"]._varSigConst),
                objName=obj.get_vhdl_name(x["symbol"]._Inout),
                objType=x["symbol"].__hdl_converter__.get_Name_array(x["symbol"]),
                defaults=x["symbol"].__hdl_converter__.get_default_value(x["symbol"]),
                size = obj.size
            )
        return ret

    def getHeader(self,obj, name,parent):
        return "-- v_list getHeader\n"    
    
    def recordMember(self,obj, name,parent,Inout=None):
        ret =""
        if not parent._issubclass_("v_class"):
            return ""
        obj1 =obj.Internal_Type.__hdl_converter__.extract_conversion_types(obj.Internal_Type)
        for x in obj1:

            ret += """{objName} : {objType}({size} - 1 downto 0)""".format(
                objName=name,
                objType=x["symbol"].__hdl_converter__.get_Name_array(x["symbol"]),
                size = obj.size
            )
        return ret
    
    def recordMemberDefault(self, obj, name,parent,Inout=None):
        ret =""
        if not parent._issubclass_("v_class"):
            return ""
        obj1 =obj.Internal_Type.__hdl_converter__.extract_conversion_types(obj.Internal_Type)
        for x in obj1:

            ret += """{objName} => (others => {defaults})""".format(
                objName=name,
                defaults=x["symbol"].__hdl_converter__.get_default_value(x["symbol"]),
                size = obj.size
            )
        return ret
        
    
    def _vhdl_slice(self,obj, sl,astParser=None):
        if issubclass(type(sl),argg_hdl_base0):
            sl = sl.__hdl_converter__._vhdl__getValue(sl,ReturnToObj=v_int(),astParser=astParser)
        
        ret = v_copy(obj.Internal_Type)
        ret._varSigConst = obj._varSigConst
        ret.__hdl_name__ =  obj.__hdl_name__+"("+str(sl)+")"
        
        self.obj_list.append(ret)

        return ret
    def get_process_header(self,obj):
        ret =""

        obj1 =obj.Internal_Type.__hdl_converter__.extract_conversion_types(obj.Internal_Type)
        
        for x in obj1:
            if x["symbol"]._varSigConst != varSig.variable_t:
                continue

            ret += """  {VarSymb} {objName} : {objType}({size} - 1 downto 0)  := (others => {defaults});\n""".format(
                VarSymb=get_varSig(x["symbol"]._varSigConst),
                objName=obj.get_vhdl_name(x["symbol"]._Inout),
                objType=x["symbol"].__hdl_converter__.get_Name_array(x["symbol"]),
                defaults=x["symbol"].__hdl_converter__.get_default_value(x["symbol"]),
                size = obj.size
            )
        return ret
        
    def to_arglist(self,obj, name,parent,withDefault = False,astParser=None):
        return name +" : " + obj.__hdl_converter__.InOut_t2str(obj)+"  " +obj.get_type()


    def _vhdl__reasign(self, obj, rhs, context=None):
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

T = TypeVar('T')      
class v_list(argg_hdl_base, Generic[T]):
    def __init__(self,Internal_Type : T,size: int,varSigConst=None ):
        super().__init__()
        self.__hdl_converter__ = v_list_converter()
        self.Internal_Type = Internal_Type
        self.driver = None
        self.content = []
        self._Inout  = InOut_t.Internal_t
        self.__Driver__ = None
        for i in range( value(size)):
            self.content.append( v_copy(Internal_Type) )

        self.size = size
        self._varSigConst = get_value_or_default(varSigConst, getDefaultVarSig())
        self.__hdl_name__ = None
        self._type = self.Internal_Type.__hdl_converter__.get_type_simple(self.Internal_Type)+"_a"

    def append(self, obj):
        self.content.append(obj)
        self.size = len(self.content)

    def set_vhdl_name(self,name, Overwrite = False):
        if self.__hdl_name__ and self.__hdl_name__ != name and not Overwrite:
            raise Exception("double Conversion to vhdl")
        
        self.__hdl_name__ = name

    def get_size(self):
        return self.size

    def get_type(self):
        return self._type

    def __getitem__(self,sl) -> T:
        return self.content[value(sl)]

    def set_simulation_param(self,module, name,writer):
        i = 0
        for x in self.content:
            x.set_simulation_param(module+"."+name, name+"(" +str(i)+")",writer)
            i+=1

    def setInout(self,Inout):
        self._Inout = Inout

    def set_varSigConst(self, varSigConst):
        self._varSigConst = varSigConst
        self.Internal_Type.set_varSigConst(varSigConst)
        for x in self.content:
            x.set_varSigConst(varSigConst)

    def __lshift__(self, rhs) -> None:
        if len(self.content) != len(rhs.content):
            raise Exception("Differnt list size")

        for x in range(len(self.content)):
            self.content[x] << rhs.content[x]

    def _sim_set_push_pull(self, Pull_list, Push_list):
        for x in self.content:
            x._sim_set_push_pull( Pull_list, Push_list)


    def get_master(self):
        master_t =  self.Internal_Type.get_master() 
        ret = v_list(master_t,0,master_t._varSigConst)
        for x in self.content:
            ret.append(x.get_master() )

        ret.driver = self
        return ret


    def get_slave(self):
        master_t =  self.Internal_Type.get_slave() 
        ret = v_list(master_t,0,master_t._varSigConst)
        for x in self.content:
            ret.append(x.get_slave())
        
        ret.driver = self
        return ret

    def __str__(self):
        return str(self.__hdl_name__)
        
    def __len__(self):
        return len(self.content)

    def getMember(self,InOut_Filter=None, VaribleSignalFilter = None):
        ret = []
        i = 0
        for x in self.content:
            x.set_vhdl_name(str(self)+"("+str(i)+")",True)
            ret.append({
                "name" : str(self)+"("+str(i)+")",
                "symbol" : x
            })
            i+=1 

        return ret

        
    def get_vhdl_name(self,Inout=None):
        if Inout is None:
            return self.__hdl_name__

        if Inout== InOut_t.input_t:
            return self.__hdl_name__+"_s2m"
        
        if Inout== InOut_t.output_t:
            return self.__hdl_name__+"_m2s"
        
        return self.__hdl_name__

    def _sim_append_update_list(self,up):
        for x in self.content:
            x._sim_append_update_list(up)

    def _issubclass_(self,test):
        if super()._issubclass_(test):
            return True
        return "v_list" == test

    def isInOutType(self,Inout):
        if Inout is None:
            return True
        if self._Inout == InOut_t.InOut_tt:
            return True

        return self._Inout == Inout

    def isVarSigType(self, varSigType):
        if varSigType is None:
            return True

        return self._varSigConst == varSigType
