import os
import sys
import inspect


from argg_hdl.argg_hdl_base import *
from argg_hdl.argg_hdl_simulation import *


class v_symbol_converter(hdl_converter_base):
    def __init__(self,inc_str):
        super().__init__()
        self.inc_str  = inc_str

    def get_dependency_objects(self, obj, depList):
        return obj
        
    def includes(self,obj, name,parent):
        ret = slv_includes
        ret += self.inc_str
        return ret

    def get_get_call_member_function(self, obj, name, args):
        ret = None
        args = [x.get_symbol() for x in args ]
        if name =="reset":
            ret = {
            "name" : name,
            "args": args,
            "self" :obj,
            "call_func" : call_func_symb_reset,
            "func_args" : None,
            "setDefault" : False

        }
        return ret
        
    def recordMember(self,obj, name, parent,Inout=None):
        if parent._issubclass_("v_class"):
            return name + " : " +obj._type

        return ""

    def recordMemberDefault(self, obj,name,parent,Inout=None):
        if parent._issubclass_("v_class"):
            return name + " => " + obj.DefaultValue 

        return ""

    def getHeader(self, obj,name,parent):
        if obj.__hdl_name__:
            name = obj.__hdl_name__

        if parent._issubclass_("v_class"):
             return ""
            
        return name + " : " +obj._type +" := " +  obj.DefaultValue  + "; \n"

    def getFuncArg(self,obj, name,parent):
        return name + " : " + obj._type   

    def _vhdl_slice(self,obj,sl,astParser=None):
        obj._add_input()
        if "std_logic_vector" in obj._type:
            ret = v_sl(obj._Inout)
            ret.__hdl_name__ = obj.__hdl_name__+"("+str(sl)+")"
            return ret

        raise Exception("unexpected type")


    def _vhdl__compare_int(self,obj, ops, rhs):
        return str(obj) + " "+ obj.__hdl_converter__.ops2str(ops) +" " +   str(rhs)

    def _vhdl__compare_std_logic(self,obj, ops, rhs):
        value = str(rhs).lower()
        if value == "true":
            rhs = "1"
        elif value == "false":
            rhs = "0"            
        return str(obj) + " "+ obj.__hdl_converter__.ops2str(ops) +" '" +  str(rhs) +"'"
    
    def _vhdl__compare_std_logic_vector(self,obj, ops, rhs):
        return str(obj) + " "+ obj.__hdl_converter__.ops2str(ops) +" " +   str(rhs)

    def _vhdl__compare(self,obj, ops, rhs):
        obj._add_input()
        if issubclass(type(rhs),argg_hdl_base):
            rhs._add_input()
    
        if obj._type == "integer":
            return obj.__hdl_converter__._vhdl__compare_int(obj, ops, rhs)
        
        if obj._type == "std_logic":
            return obj.__hdl_converter__._vhdl__compare_std_logic(obj, ops, rhs)
        
        if "std_logic_vector" in obj._type:
            return obj.__hdl_converter__._vhdl__compare_std_logic_vector(obj, ops, rhs)
        
        return str(obj) + " "+ obj.__hdl_converter__.ops2str(ops)+" " +   str(rhs)

    def _to_hdl___bool__(self,obj, astParser):
        obj._add_input()
        if obj._type == "std_logic":
            return str(obj) + " = '1'"
        if "std_logic_vector" in obj._type:
            return str(obj) + " > 1"
        if obj._type == "boolean":
            return str(obj)
        if obj._type == "integer":
            return str(obj) + " > 0"

        return "to_bool(" + str(obj) + ") "

    def _vhdl__DefineSymbol(self,obj, VarSymb=None):
        print("_vhdl__DefineSymbol is deprecated")
        if not VarSymb:
            VarSymb = get_varSig(obj._varSigConst)

        if  obj.__Driver__ is not None and str(obj.__Driver__ ) != 'process':
            return ""
        name = obj.__hdl_name__

            
        return  VarSymb+ " " + name + " : " +obj._type +" := " +  obj.DefaultValue  + "; \n"
    def get_architecture_header(self, obj):

        if obj._Inout != InOut_t.Internal_t and not obj.__isInst__:
            return ""
        
        if obj._varSigConst == varSig.variable_t:
            return ""
        
        
        VarSymb = get_varSig(obj._varSigConst)

        #if  obj.__Driver__ != None and str(obj.__Driver__ ) != 'process':
        #    return ""
        name = obj.__hdl_name__

        ret = "  " + VarSymb+ " " + name + " : " +obj._type +" := " +  obj.DefaultValue  + "; \n"   
        return  ret

    def get_port_list(self,obj):
        ret = []
        if obj._Inout == InOut_t.Internal_t:
            return ret
        
        if obj._varSigConst != varSig.signal_t:
            return ret
        
        ret.append( obj.__hdl_name__ + " : "+ obj.__hdl_converter__.InOut_t2str(obj) + " " + obj._type + " := " + obj.DefaultValue)
        return ret


    def _vhdl__reasign_std_logic(self, obj, rhs, target, astParser=None,context_str=None):
        asOp = obj.__hdl_converter__.get_assiment_op(obj)
        if issubclass(type(rhs),argg_hdl_base0):
            return target + asOp + str(rhs.__hdl_converter__._vhdl__getValue(rhs, obj._type)) 
        return target + asOp+  str(rhs) 

    def _vhdl__reasign_std_logic_vector(self, obj, rhs, target, astParser=None,context_str=None):
        asOp = obj.__hdl_converter__.get_assiment_op(obj)
        if str(rhs) == '0':
            return target + asOp+ " (others => '0')"
        
        if  issubclass(type(rhs),argg_hdl_base):
            return target + asOp +  str(rhs.__hdl_converter__._vhdl__getValue(rhs, obj._type)) 
        
        if  type(rhs).__name__=="v_Num":
            return  """{dest} {asOp} std_logic_vector(to_unsigned({src}, {dest}'length))""".format(
                dest=target,
                src = str(rhs.value),
                asOp=asOp
            )
    def _vhdl__reasign_int(self, obj, rhs, target, astParser=None,context_str=None):
        asOp = obj.__hdl_converter__.get_assiment_op(obj)
        if str(rhs) == '0':
            return target + asOp+ " 0"
        if type(rhs).__name__ == "str":
            return target + asOp+ str(rhs)
                
        if rhs._type == "integer":
            return target + asOp+ str(rhs)
        if "std_logic_vector" in rhs._type:
            return target + asOp +" to_integer(signed("+ str(rhs)+"))"
        
        return target +asOp +  str(rhs)

    def _vhdl__reasign(self, obj, rhs, astParser=None,context_str=None):
        obj._add_output()
        target = str(obj)
        if obj._varSigConst == varSig.signal_t and not (context_str and (context_str == "archetecture" or context_str== "process")):
            target = target.replace(".","_")

        if issubclass(type(rhs),argg_hdl_base0)  and str( obj.__Driver__) != 'process':
            obj.__Driver__ = rhs
        
        if isProcess():
            obj.__Driver__ = 'process'
        
        if obj._type == "std_logic":
            return obj.__hdl_converter__._vhdl__reasign_std_logic(obj, rhs,target, astParser,context_str)
        
        if "std_logic_vector" in obj._type:
            return obj.__hdl_converter__._vhdl__reasign_std_logic(obj, rhs,target, astParser,context_str)
        
        if obj._type == "integer":
            return obj.__hdl_converter__._vhdl__reasign_int(obj, rhs,target, astParser,context_str)

        asOp = obj.__hdl_converter__.get_assiment_op(obj)            
        return target +asOp +  str(rhs)
    
    def get_type_simple(self,obj):
        ret = obj._type
        if "std_logic_vector" in ret:
            sp1 = int(ret.split("downto")[0].split("(")[1])
            sp2 = int(ret.split("downto")[1].split(")")[0])
            sp3 = sp1 -sp2 +1
            ret  = "slv"+str(sp3)
        return ret

    def _vhdl__getValue(self,obj, ReturnToObj=None,astParser=None):
        obj._add_input()
        if ReturnToObj == "integer" and  "std_logic_vector" in obj._type:
            return  "to_integer(signed( " + str(obj)  + "))"
        
        return obj

    def get_default_value(self,obj):
        return obj.DefaultValue

    def length(self,obj):
        ret = v_int()
        ret.__hdl_name__=str(obj)+"'length"
        return ret

    def to_arglist(self,obj, name,parent,withDefault = False):
        inoutstr = obj.__hdl_converter__.InOut_t2str(obj)
        varSigstr = ""
        if obj._varSigConst == varSig.signal_t:
            varSigstr = "signal "

        if not inoutstr:
            inoutstr = ""
        default_str = ""
        if withDefault and obj.__writeRead__ != InOut_t.output_t and obj._Inout != InOut_t.output_t:
            default_str =  " := " + obj.__hdl_converter__.get_default_value(obj)

        return varSigstr + name + " : " + inoutstr +" " + obj.getType() + default_str

class v_symbol(argg_hdl_base):
    __value_list__ = []
    def __init__(self, v_type, DefaultValue, Inout = InOut_t.Internal_t,includes="",value=None,varSigConst=varSig.variable_t):
        super().__init__()
        if not varSigConst:
            varSigConst = getDefaultVarSig()

        self.__hdl_converter__= v_symbol_converter(includes)
        self._type = v_type
        self.DefaultValue = str(DefaultValue)
        self._Inout = Inout
        

        self.__hdl_name__ = None
        self.__value_list__.append(get_value_or_default(value, DefaultValue))
        self.__value_Index__ = len(self.__value_list__) -1
        #self.value = get_value_or_default(value, DefaultValue)
        self.nextValue  = get_value_or_default(value, DefaultValue)
        self._varSigConst=varSigConst
        self.__Driver__ = None 
        self.__update_list__ = list()
        self.__update__list_process__ = list()
        self.__update__list_running__ =[]
        self.__update__list_process_running__ = list()
        self.__receiver_list_running__ = []
        self.__got_update_list__ = False
        self.__Pull_update_list__ = list()
        self.__Push_update_list__ = list()
        self.__vcd_varobj__ = None
        self.__vcd_writer__ = None
        self.__UpdateFlag__ = False
        self._Simulation_name = "NotSet"





    def _sim_get_value(self):
        return self.__value_list__[self.__value_Index__]


    def isInOutType(self, Inout):
        if Inout is None:
            return True
        if self._Inout == InOut_t.InOut_tt:
            return True

        return self._Inout == Inout

    def isVarSigType(self, varSigType):
        if varSigType is None:
            return True

        return self._varSigConst == varSigType



    def set_vhdl_name(self,name, Overwrite = False):
        if self.__hdl_name__ and self.__hdl_name__ != name and not Overwrite:
            raise Exception("double Conversion to vhdl")
        
        self.__hdl_name__ = name




    def getType(self,Inout=None):
        return self._type

    def getTypes(self):
        return {
            "main" : self._type
        }
    def resetInout(self):
        self._Inout = InOut_t.Internal_t
        
    def setInout(self,Inout):
        if self._Inout == InOut_t.Internal_t and  Inout == InOut_t.Master_t:
            self._Inout = InOut_t.output_t
            return 
        
        if Inout == InOut_t.Master_t:
            return 

        if self._Inout == InOut_t.Internal_t and  Inout == InOut_t.Slave_t:
            self._Inout = InOut_t.input_t
            return 
        
        if Inout == InOut_t.Slave_t:
            self._Inout = InoutFlip(self._Inout)
            return 
        self._Inout = Inout


    def set_varSigConst(self, varSigConst):
        self._varSigConst = varSigConst
        
    
    def flipInout(self):
        self._Inout = InoutFlip(self._Inout)

    
    

    def get_type(self):
        return self._type



    def __str__(self):
        if self.__hdl_name__:
            return str(self.__hdl_name__)

        raise Exception("No Name was given to symbol")

    def __repr__(self):
        return str(value(self))
        
    def set_simulation_param(self,module, name,writer):
        self._Simulation_name =module+"." +name
        self.__vcd_varobj__ = writer.register_var(module, name, 'integer', size=32)
        self.__vcd_writer__ = writer 
        self.__hdl_name__ = name
        self.__vcd_writer__.change(self.__vcd_varobj__, self._sim_get_value())

    def _sim_write_value(self):
        if self.__vcd_writer__:
            self.__vcd_writer__.change(self.__vcd_varobj__, self._sim_get_value())
        
        for x in self.__receiver_list_running__:
            x._sim_write_value()

    def update_init(self):# Only needs to run once on init
        if not self.__got_update_list__:
            self.__update__list_process_running__ = list(set(self._sim__update_list_process()))
            self.__update__list_running__ =     list(set(self._sim_get_update_list()))
            self.__receiver_list_running__  = self._sim_get_receiver()
            self.__got_update_list__ = True


    def update(self):
        self.update_init() # Wrong Place here but it works 

        self.__value_list__[self.__value_Index__]  = self.nextValue

        self._sim_write_value()
        
        gsimulation.append_updateList(self.__update__list_running__)
        gsimulation.append_updateList_process(self.__update__list_process_running__)

        self.__UpdateFlag__ = False

##################### Operators #############################################
    def __add__(self,rhs):
        
        return value(self) + value(rhs) 

    def __sub__(self,rhs):
        
        return value(self) - value(rhs) 
        
    def __lt__(self,rhs):
        return value(self) < value(rhs) 

    def __gt__(self,rhs):
        return value(self) > value(rhs) 

    def __eq__(self,rhs):
        return value(self) == value(rhs) 
##################### End Operators #############################################

    def _sim_get_new_storage(self):
        self.__value_list__.append(value(self))
        self.__value_Index__ = len(self.__value_list__) -1  

    def _sim_get_update_list(self):
        ret = self.__update_list__
        for x in self.__receiver__:
            ret += x._sim_get_update_list()
        return ret
    def _sim_get_receiver(self):
        ret = self.__receiver__
        for x in self.__receiver__:
            ret += x.__receiver__
        return ret
    
    def _sim_get_primary_driver(self):
        ret = self
        if self.__Driver__:
            ret = self.__Driver__._sim_get_primary_driver()
        return ret

    def _sim_set_new_value_index(self,Index):
        self.__value_Index__ = Index
        receivers = self._sim_get_receiver()
        for x in receivers:
            x.__value_Index__ = self.__value_Index__
    
    def _sim__update_list_process(self):
        ret = self.__update__list_process__
        for x in self.__receiver__:
            ret += x._sim__update_list_process()
        return ret

    def _sim_start_simulation(self):
        self.__update__list_process_running__ = self._sim__update_list_process()
        self.__update__list_running__ =self._sim_get_update_list()


    def _sim_append_update_list(self,up):
        self.__update_list__.append(up)
    


    def _instantiate_(self):
        self.__isInst__ = True
        self._Inout = InoutFlip(self._Inout)
        return self
        
    def _un_instantiate_(self, Name = ""):
        self.__isInst__ = False
        self.flipInout()
        self.set_vhdl_name(Name,True)
        return self

    def __bool__(self):
        return value(self) > 0

    def reset(self):
        self << 0
    def _Connect_running(self, rhs):
        self.nextValue = value(rhs)
        #print("assing: ", self.__value_Index__ , self._Simulation_name ,  value(rhs))

        if self.nextValue !=  value(self):
            def update():
                self.update()

            if not self.__UpdateFlag__:
                gsimulation.append_updateList([update])
                self.__UpdateFlag__ = True
                
        if self._varSigConst == varSig.variable_t:
            self.__value_list__[self.__value_Index__]  = self.nextValue

    def _Conect_Not_running(self,rhs):
        if self.__Driver__ is not None and not isConverting2VHDL():#todo: there is a bug with double assigment in the conversion to vhdl
            raise Exception("symbol has already a driver", str(self))
        
        if not issubclass(type(rhs),argg_hdl_base0):
            self.nextValue = rhs
            self.__value_list__[self.__value_Index__] = rhs
            return

        if rhs._varSigConst == varSig.variable_t or self._varSigConst == varSig.variable_t:
            self.__value_list__[self.__value_Index__] = value(rhs)
            def update1():
                #print("update: ", self.__value_Index__ , self._Simulation_name ,  value(rhs))
                self.nextValue = value(rhs)
                self.update()
            rhs.__update_list__.append(update1)
        else:
            self.__Driver__ = rhs
            rhs.__receiver__.append(self)
            self.nextValue = rhs.nextValue
            self._sim_set_new_value_index(  rhs._sim_get_primary_driver().__value_Index__ )

        
        
    def __lshift__(self, rhs):
        if gsimulation.isRunning():
            self._Connect_running(rhs)
        else:
            self._Conect_Not_running(rhs)
            





    def _issubclass_(self,test):
        if super()._issubclass_(test):
            return True
        return "v_symbol" == test












slv_includes = """
library IEEE;
library UNISIM;
library work;
  use IEEE.numeric_std.all;
  use IEEE.std_logic_1164.all;
  use UNISIM.VComponents.all;
  use ieee.std_logic_unsigned.all;
  use work.argg_hdl_core.all;
"""


def v_bool(Inout=InOut_t.Internal_t,Default=0,varSigConst=None):
    value = Default
    if type(Default).__name__ == "int":
        Default = "'" + str(Default) +"'"
    

    return v_symbol(
        v_type= "boolean", 
        DefaultValue=Default, 
        Inout = Inout,
        includes=slv_includes,
        value = value,
        varSigConst=varSigConst
    )
 
def v_sl(Inout=InOut_t.Internal_t,Default=0,varSigConst=None):
    value = Default
    if type(Default).__name__ == "int":
        Default = "'" + str(Default) +"'"
    

    return v_symbol(
        v_type= "std_logic", 
        DefaultValue=Default, 
        Inout = Inout,
        includes=slv_includes,
        value = value,
        varSigConst=varSigConst
    )

def v_slv(BitWidth=None,Default=0, Inout=InOut_t.Internal_t,varSigConst=None):


    value = Default
    if str(Default) == '0':
        Default = "(others => '0')"

    elif type(Default).__name__ == "int":
        Default =  'x"'+ hex(Default)[2:].zfill(int( int(BitWidth)/4))+'"'  
    
    v_type = ""
    if BitWidth is None:
        v_type="std_logic_vector"    
    elif type(BitWidth).__name__ == "int":
        v_type="std_logic_vector(" + str(BitWidth -1 ) + " downto 0)"
    else: 
        v_type = "std_logic_vector(" + str(BitWidth ) + " -1 downto 0)"

    return v_symbol(
        v_type=v_type, 
        DefaultValue=Default,
        value=value,
        Inout=Inout,
        includes=slv_includes,
        varSigConst=varSigConst
    )

def v_int(Default=0, Inout=InOut_t.Internal_t, varSigConst=None):
    
    return v_symbol(
        v_type= "integer",
        value= value(Default), 
        DefaultValue=str(Default), 
        Inout = Inout,
        includes=slv_includes,
        varSigConst=varSigConst
    )

def call_func_symb_reset(obj, name, args, astParser=None,func_args=None):
    asOp = args[0].__hdl_converter__.get_assiment_op(args[0])
    val = None
    if obj._type == "std_logic":
        val = "'0'"
    if "std_logic_vector" in obj._type:
        val = "(others => '0')"
    if obj._type == "integer":
        val = '0'
    
    if val is None:
        raise Exception("unable to reset symbol")
    ret =  str(args[0])  + asOp + val
    return ret
