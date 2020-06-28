from __future__ import annotations
import os
import sys
import inspect

from argg_hdl.argg_hdl_base import *
from argg_hdl.argg_hdl_simulation import *

from argg_hdl.argg_hdl_slice_base import v_slice_base, slice_helper


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
    def _vhdl__call_member_func(self, obj, name, args, astParser=None):
        
        call_obj = obj.__hdl_converter__.get_get_call_member_function(obj, name, args)
        
        args_str = [str(x.get_type()) for x in args]
        args_str=join_str(args_str, Delimeter=", ")
        if call_obj is None:
            primary.__hdl_converter__.MissingTemplate=True
            astParser.Missing_template = True

            print_cnvt(str(gTemplateIndent)+'<Missing_Template function="' + str(name) +'" args="' +args_str+'" />' )
            return None

        print_cnvt(str(gTemplateIndent)+'<use_template function ="' + str(name)  +'" args="' +args_str+'" />'  )
        call_func = call_obj["call_func"]
        if call_func:
            return call_func(obj, name, args, astParser, call_obj["func_args"])

        primary.__hdl_converter__.MissingTemplate=True
        astParser.Missing_template = True
        return None

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
            "setDefault" : False,
            "varSigIndependent" : True

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
        astParser.add_read(obj)
        obj._add_input()
        if "std_logic_vector" in obj._type:
            if type(sl).__name__ == "v_slice":
                ret = v_slv( Inout = obj._Inout,varSigConst=obj._varSigConst)
                ret.__hdl_name__ = obj.__hdl_name__+"("+str(sl)+")"
            else:
                ret = v_sl(Inout=obj._Inout, varSigConst=obj._varSigConst)
                index = sl.__hdl_converter__._vhdl__getValue(sl,__slice_type__)
                ret.__hdl_name__ = obj.__hdl_name__+"("+str(index)+")"
            
            
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

    def _vhdl__compare(self,obj, ops, rhs, astParser):
        astParser.add_read(obj)
        obj._add_input()
        if issubclass(type(rhs),argg_hdl_base):
            astParser.add_read(rhs)
            rhs._add_input()
    
        if obj._type == "integer":
            return obj.__hdl_converter__._vhdl__compare_int(obj, ops, rhs)
        
        if obj._type == "std_logic":
            return obj.__hdl_converter__._vhdl__compare_std_logic(obj, ops, rhs)
        
        if "std_logic_vector" in obj._type:
            return obj.__hdl_converter__._vhdl__compare_std_logic_vector(obj, ops, rhs)
        
        return str(obj) + " "+ obj.__hdl_converter__.ops2str(ops)+" " +   str(rhs)

    def _to_hdl___bool__(self,obj:v_symbol, astParser):
        obj._add_input()
        astParser.add_read(obj)
        if obj._type == "std_logic":
            return str(obj) + " = '1'"
        if "std_logic_vector" in obj._type:
            return str(obj) + " > 0"
        if obj._type == "boolean":
            return str(obj)
        if obj._type == "integer":
            return str(obj) + " > 0"

        return "to_bool(" + str(obj) + ") "

    def _vhdl__BitAnd(self,obj:"v_symbol",rhs,astParser) -> "v_symbol":
        ret = v_slv()
        ret.set_vhdl_name(str(obj)+ " & " +str(rhs) ,True)
        return ret

    def _vhdl__DefineSymbol(self,obj:"v_symbol", VarSymb=None):
        print_cnvt("_vhdl__DefineSymbol is deprecated")
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

    def get_port_list(self,obj:"v_symbol"):
        ret = []
        if obj._Inout == InOut_t.Internal_t:
            return ret
        
        if obj._varSigConst != varSig.signal_t:
            return ret
        
        ret.append( obj.__hdl_name__ + " : "+ obj.__hdl_converter__.InOut_t2str(obj) + " " + obj._type + " := " + obj.DefaultValue)
        return ret


    def _vhdl__reasign_std_logic(self, obj:"v_symbol", rhs, target, astParser=None,context_str=None):
        asOp = obj.__hdl_converter__.get_assiment_op(obj)
        if issubclass(type(rhs),argg_hdl_base0):
            return target + asOp + str(rhs.__hdl_converter__._vhdl__getValue(rhs, obj)) 
        return target + asOp+  str(rhs) 

    def _vhdl__reasign_std_logic_vector(self, obj:"v_symbol", rhs, target, astParser=None,context_str=None):
        asOp = obj.__hdl_converter__.get_assiment_op(obj)
        if str(rhs) == '0':
            return target + asOp+ " (others => '0')"
        
        if  issubclass(type(rhs),argg_hdl_base):
            if rhs.get_type() == 'integer':
                return  """{dest} {asOp} std_logic_vector(to_unsigned({src}, {dest}'length))""".format(
                    dest=target,
                    src = str(rhs),
                    asOp=asOp
                )

            return target + asOp +  str(rhs.__hdl_converter__._vhdl__getValue(rhs, obj,astParser=astParser)) 
        
        if  type(rhs).__name__=="v_Num":
            return  """{dest} {asOp} std_logic_vector(to_unsigned({src}, {dest}'length))""".format(
                dest=target,
                src = str(rhs.value),
                asOp=asOp
            )

        rhs_str = str(rhs)
        if rhs_str.isnumeric():
            return  """{dest} {asOp} std_logic_vector(to_unsigned({src}, {dest}'length))""".format(
                dest=target,
                src = rhs_str,
                asOp=asOp
            )

        return target + asOp+  str(rhs) 

    def _vhdl__reasign_int(self, obj:"v_symbol", rhs, target, astParser=None,context_str=None):
        asOp = obj.__hdl_converter__.get_assiment_op(obj)

        if issubclass(type(rhs),argg_hdl_base) and "std_logic_vector" in rhs._type:
            return target + asOp +" to_integer(signed("+ str(rhs)+"))"
        
        return target +asOp +  str(rhs)

    def _vhdl__reasign(self, obj:"v_symbol", rhs, astParser=None,context_str=None):
        if astParser:
            astParser.add_write(obj)
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
            return obj.__hdl_converter__._vhdl__reasign_std_logic_vector(obj, rhs,target, astParser,context_str)
        
        if obj._type == "integer":
            return obj.__hdl_converter__._vhdl__reasign_int(obj, rhs,target, astParser,context_str)

        asOp = obj.__hdl_converter__.get_assiment_op(obj)            
        return target +asOp +  str(rhs)
    

    def _vhdl__reasign_rshift__slv(self, obj, rhs, astParser=None,context_str=None):
        rhs._add_output()
        asOp = rhs.__hdl_converter__.get_assiment_op(rhs)            
        return str(rhs)+"("+ str(rhs) +"'range)" +asOp +  str(obj)+"("+ str(rhs) +"'range)" 

    def _vhdl__reasign_rshift_(self, obj, rhs, astParser=None,context_str=None):
        if issubclass(type(obj),argg_hdl_base0) and issubclass(type(rhs),argg_hdl_base0):
            if "std_logic_vector" in obj._type and "std_logic_vector" in rhs._type:
                return self._vhdl__reasign_rshift__slv(obj, rhs,astParser,context_str)

        return hdl._vhdl__reasign(rhs, obj,astParser,context_str)

    def get_type_simple(self,obj:"v_symbol"):
        ret = obj._type
        if "std_logic_vector" in ret:
            sp1 = int(ret.split("downto")[0].split("(")[1])
            sp2 = int(ret.split("downto")[1].split(")")[0])
            sp3 = sp1 -sp2 +1
            ret  = "slv"+str(sp3)
        return ret

    def _vhdl__getValue(self,obj:"v_symbol", ReturnToObj=None,astParser=None):
        if astParser:
            astParser.add_read(obj)
        obj._add_input()
        if ReturnToObj.get_type() ==  obj._type:
            return obj
        if obj._varSigConst ==varSig.unnamed_const:
            if ReturnToObj.get_type() == "std_logic":
                obj.__hdl_name__="'" + str(obj)  + "'"
                obj._type= "std_logic"
                return  obj
        if ReturnToObj.get_type() == "integer" and  "std_logic_vector" in obj._type:
            return  "to_integer(signed( " + str(obj)  + "))"
        if ReturnToObj.get_type() == "uinteger" and  "std_logic_vector" in obj._type:
            return  "to_integer(unsigned( " + str(obj)  + "))"
        return obj

    def get_default_value(self,obj:"v_symbol"):
        return obj.DefaultValue

    def length(self,obj:"v_symbol"):
        ret = v_int()
        ret.__hdl_name__=str(obj)+"'length"
        return ret

    def get_type_func_arg(self,obj:"v_symbol"):
        ret = obj.get_type()
        if "std_logic_vector" in ret:
            return "std_logic_vector"
        return ret
    def to_arglist(self,obj:"v_symbol", name,parent,withDefault = False,astParser=None):
        inout = astParser.get_function_arg_inout_type(obj)
        inoutstr = obj.__hdl_converter__.InOut_t2str(obj)
        varSigstr = ""
        if obj._varSigConst == varSig.signal_t:
            varSigstr = "signal "

        if not inoutstr:
            inoutstr = ""
        default_str = ""
        if withDefault and obj.__writeRead__ != InOut_t.output_t and obj._Inout != InOut_t.output_t:
            default_str =  " := " + obj.__hdl_converter__.get_default_value(obj)

        return varSigstr + name + " : " + inoutstr +" " + obj.__hdl_converter__.get_type_func_arg(obj) + default_str

def v_symbol_reset():
    #v_symbol.__value_list__.clear()
    pass

class v_symbol(argg_hdl_base):
    __value_list__ = []
    
    def __init__(self, v_type, DefaultValue, Inout = InOut_t.Internal_t,includes="",value=None,varSigConst=varSig.variable_t, Bitwidth=32):
        super().__init__()
        if not varSigConst:
            varSigConst = getDefaultVarSig()

        self.Bitwidth = Bitwidth
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
        self.__vcd_varobj__ = writer.register_var(module, name, 'integer', size=self.Bitwidth)
        self.__vcd_writer__ = writer 
        self.__hdl_name__ = name
        self.__vcd_writer__.change(self.__vcd_varobj__, self._sim_get_value())

    def _sim_write_value(self):
        if self.__vcd_writer__:
            self.__vcd_writer__.change(self.__vcd_varobj__, self._sim_get_value())
        
        for x in self.__receiver_list_running__:
            x._sim_write_value()

    def update_init(self):# Only needs to run once on init
        if self.__got_update_list__:
            return 
        
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

    def __ge__(self,rhs):
        return value(self) >= value(rhs) 
    
    def __le__(self,rhs):
        return value(self) <= value(rhs) 

    def __eq__(self,rhs):
        return value(self) == value(rhs) 
    
    def __getitem__(self, b):
        if type(b).__name__ == 'slice':
            start = b.start
            stop = b.stop
        else:
            start = value(b)
            stop = start+1
        if stop is None:
            stop = len(self) - 1

        stop = min(value(stop),  len(self) - 1)
        sl = slice_helper(start=start,stop=stop)
        return v_slice_base(self,sl)
        
        
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
            ret += x._sim_get_receiver()
        return ret
    
    def _sim_get_primary_driver(self):
        ret = self
        if self.__Driver__ and not isinstance(self.__Driver__,str):
            ret = self.__Driver__._sim_get_primary_driver()
        return ret

    def _sim_set_new_value_index(self,Index):
        self.__value_Index__ = Index
        receivers = self._sim_get_receiver()
        for x in receivers:
            x._sim_set_new_value_index(self.__value_Index__)
    
    def _sim__update_list_process(self):
        ret = self.__update__list_process__
        for x in self.__receiver__:
            ret += x._sim__update_list_process()
        return ret




    def _sim_append_update_list(self,up):
        self.__update_list__.append(up)
    


    def _instantiate_(self):
        self.__isInst__ = True
        self.flipInout()
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
            self.DefaultValue  = rhs
            self.__Driver__ = v_int(rhs,varSigConst = varSig.unnamed_const )
            self.__Driver__.__hdl_name__ = str(rhs)
            
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
        elif isFunction():
            pass
        else:
            self._Conect_Not_running(rhs)
            
    def __len__(self):
        return self.Bitwidth
    def __and__(self, rhs):
        bitShift = len(rhs)
        v  = value(self) << bitShift
        v += value(rhs)
        sl= slice_helper(start=0,stop=len(rhs)+len(self)-1)
        ret = v_slice_base(v,sl)
        return ret
        


    def __int__(self):
        return value(self)


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
        varSigConst=varSigConst,
        Bitwidth=1
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
        varSigConst=varSigConst,
        Bitwidth=1
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
        BitWidth=32  
    elif type(BitWidth).__name__ == "int":
        v_type="std_logic_vector(" + str(BitWidth -1 ) + " downto 0)"
    else: 
        v_type = "std_logic_vector(" + str(BitWidth ) + " -1 downto 0)"
        BitWidth=32

    return v_symbol(
        v_type=v_type, 
        DefaultValue=Default,
        value=value,
        Inout=Inout,
        includes=slv_includes,
        varSigConst=varSigConst,
        Bitwidth=int(BitWidth)
    )

def v_int(Default=0, Inout=InOut_t.Internal_t, varSigConst=None,Bitwidth=32):
    
    return v_symbol(
        v_type= "integer",
        value= value(Default), 
        DefaultValue=str(Default), 
        Inout = Inout,
        includes=slv_includes,
        varSigConst=varSigConst,
        Bitwidth=Bitwidth
    )

def v_uint(Default=0, Inout=InOut_t.Internal_t, varSigConst=None,Bitwidth=32):
    
    return v_symbol(
        v_type= "uinteger",
        value= value(Default), 
        DefaultValue=str(Default), 
        Inout = Inout,
        includes=slv_includes,
        varSigConst=varSigConst,
        Bitwidth=Bitwidth
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
    args[0]._add_output()
    astParser.add_write(args[0])
    return ret

__slice_type__ = v_uint()