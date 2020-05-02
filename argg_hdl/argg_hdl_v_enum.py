import os,sys,inspect

from argg_hdl.argg_hdl_base import *
from argg_hdl.argg_hdl_v_symbol import v_symbol


class v_enum_converter(hdl_converter_base):
    def __init__(self):
        super().__init__()

    def get_type_simple(self,obj):
        return obj.name

    def getHeader(self,obj, name,parent):
        if  parent and parent._issubclass_("v_class"):
             return ""
            
        # type T_STATE is (RESET, START, EXECUTE, FINISH);
        name = obj.name
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

        h1  = obj.__hdl_converter__.getHeader(obj,None,None)
        PackageName = obj.__hdl_converter__.get_type_simple(obj)+"_pack"
        fileContent = """
library IEEE;
library UNISIM;
library work;
use IEEE.numeric_std.all;
use IEEE.std_logic_1164.all;
use UNISIM.VComponents.all;
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
    
    def recordMember(self, obj, name, parent,Inout=None):
        if parent._issubclass_("v_class"):
            if obj._Inout == InOut_t.Slave_t:
                Inout = InoutFlip(Inout)
            return name + " : " +obj.name +"; \n"
       
        return ""

    def recordMemberDefault(self, obj, name, parent,Inout=None):
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

        return VarSymb +" " +str(obj) + " : " + obj.name +" := " + obj._type(value(obj.symbol)).name +";\n"

class v_enum(argg_hdl_base):
    def __init__(self,EnumIn,EnumVal=None,name=None, Inout = InOut_t.Internal_t,includes="",value=None,varSigConst=varSig.variable_t):
        super().__init__()
        self.__hdl_converter__ = v_enum_converter()
        if type(EnumIn).__name__ == "EnumMeta":
            Enumtype = EnumIn
        elif type(type(EnumIn)).__name__ == "EnumMeta":
            Enumtype = type(EnumIn)
            EnumVal = EnumIn
            
        if EnumVal == None:
            EnumVal = Enumtype(0)

        if name == None:
            name = Enumtype.__name__

        self.symbol = v_symbol(name,EnumVal.value,Inout=Inout,includes=includes,value=EnumVal.value,varSigConst=varSigConst )
        self._type = Enumtype
        
        self.name = name
        self.__hdl_name__ = None
        self._Inout = Inout
        self._varSigConst = varSigConst

    def __lshift__(self, rhs):
        
        if isinstance(rhs,type(self)):
            self.symbol << rhs.symbol
            return 
        
        if isinstance(rhs,self._type):
            self.symbol << value(rhs)
            return 

        raise Exception("[ENUM] Unable tp connect different types", self, rhs)


        
    def _sim_get_new_storage(self):
        self.symbol._sim_get_new_storage()

    def set_simulation_param(self,module, name,writer):
        self.symbol.set_simulation_param(module, name, writer)
    
    def __repr__(self):
        ret = str(self._type(value(self.symbol)).name) +": "+ str(value(self.symbol))
        return ret
    
    def setInout(self,Inout):
        self.symbol.setInout(Inout)


    def set_varSigConst(self, varSigConst):
        self.symbol.set_varSigConst(varSigConst)

    def isVarSigType(self, varSigType):
        return self.symbol.isVarSigType( varSigType)

    def _sim_get_value(self):
        return value(self.symbol)
    
    
    def set_vhdl_name(self,name, Overwrite = False):
        if self.__hdl_name__ and self.__hdl_name__ != name and Overwrite == False:
            raise Exception("double Conversion to vhdl")
        else:
            self.__hdl_name__ = name



   
    

    def isInOutType(self, Inout):
        
        if Inout==None or self._Inout == Inout: 
            return True
        elif self._Inout== InOut_t.Master_t:
            mem = self.getMember(Inout)
            return len(mem) > 0
        elif self._Inout == InOut_t.Slave_t:
            if Inout == InOut_t.Master_t:
                Inout = InOut_t.Slave_t
            elif Inout == InOut_t.Slave_t:
                Inout = InOut_t.Master_t
            elif Inout == InOut_t.input_t:
                Inout = InOut_t.output_t
            elif Inout == InOut_t.output_t:
                Inout = InOut_t.input_t
            
            mem = self.getMember(Inout)
            return len(mem) > 0




    def __str__(self):
        if self.__hdl_name__:
            return self.__hdl_name__

        return self._type(value(self.symbol)).name 


    

    def _issubclass_(self,test):
        if super()._issubclass_(test):
            return True
        return "v_enum" == test
        
