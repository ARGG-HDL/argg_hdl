from __future__ import annotations
import os
import sys
import inspect

from argg_hdl.argg_hdl_base import *
from argg_hdl.argg_hdl_simulation import *

from argg_hdl.argg_hdl_slice_base import v_slice_base, slice_helper
from argg_hdl.argg_hdl__primitive_type_converter  import get_primitive_hdl_converter


def v_symbol_reset():
    #v_symbol.__value_list__.clear()
    pass

def get_value(symb):
    return value(symb)
class v_symbol(argg_hdl_base):
    __value_list__ = []
    
    def __init__(self, v_type, DefaultValue, Inout = InOut_t.Internal_t,includes="",value=None,varSigConst=varSig.variable_t, Bitwidth=32, primitive_type = "base",Alias=None):
        self.primitive_type = primitive_type
        if isRunning():
            self.Bitwidth = get_value( Bitwidth)
            self.nextValue  = get_value_or_default(value, DefaultValue)
            self._varSigConst= varSig.runtime_variable_t
            
            return 
            
        super().__init__()
        if not varSigConst:
            varSigConst = getDefaultVarSig()

        self.Bitwidth_raw = Bitwidth
        self.Bitwidth = get_value( Bitwidth)
        self.BitMask = 2** get_value(Bitwidth) -1

        self.nextValue  = get_value_or_default(value, DefaultValue)
        self._varSigConst=varSigConst


        self.__hdl_converter__= get_primitive_hdl_converter(get_value(primitive_type))(slv_includes)
        self.__hdl_converter__.add_alias(self,Alias)
        self._type = v_type
        
        self.DefaultValue = DefaultValue
        self._Inout = Inout
        self.__isFreeType__ = False
        

        self.__hdl_name__ = None
        self.__hdl_name_inside__ = None
        self.__hdl_name_outside__ = None
        self.__value_list__.append(get_value_or_default(value, DefaultValue))
        self.__value_Index__ = len(self.__value_list__) -1
        
            
        self.__Driver__ = None
        self.__Driver_IsInit__ = None
            
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
        if self._varSigConst==varSig.runtime_variable_t:
            return self.nextValue
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
        
        if self.__isFreeType__:
            name = name.replace(".","_")

        self.__hdl_name__ = name
        if self.__isInst__:
            self.__hdl_name_outside__ = name      
        else:
            self.__hdl_name_inside__ = name
        




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


    def __Get_Driver_in_scope__(self):
        if self._Inout == InOut_t.input_t:
            return self, None
        if self.__Driver__ is None:
            return self, None
        if self.__Driver__._varSigConst != varSig.signal_t:
             return self, None 
        if self.__Driver__._Inout == InOut_t.input_t:
            return self.__Driver__, self.__Driver_IsInit__ 
        
        if self.__Driver__._Inout == InOut_t.output_t:
            return self.__Driver__ , self.__Driver_IsInit__ 

        return self.__Driver__.__Get_Driver_in_scope__()

    def __str__(self):
        if self.__isFreeType__:
            driver,IsInit  = self.__Get_Driver_in_scope__()

            if IsInit is None and  driver.__hdl_name__:
                return driver.__hdl_name__
            
            if IsInit  and  driver.__hdl_name_outside__:
                return driver.__hdl_name_outside__
                        
            if not IsInit  and  driver.__hdl_name_inside__:
                return driver.__hdl_name_inside__

        elif self.__hdl_name__:
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
        
    def __mul__(self, rhs):
        return value(self) * value(rhs) 

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
            stop = len(self)

        stop = min(value(stop),  len(self) )
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

    def _Connect_running_runtime_variable(self, rhs):
        self.nextValue = value(rhs)
       
    def _Connect_running(self, rhs):
        val = value(rhs) 
        sign = 1 if val > 0 else -1
        self.nextValue =sign*( abs(val) & self.BitMask)
       

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
            self.__Driver_IsInit__  = rhs.__isInst__
            rhs.__receiver__.append(self)
            self.nextValue = rhs.nextValue
            self._sim_set_new_value_index(  rhs._sim_get_primary_driver().__value_Index__ )

        
        
    def __lshift__(self, rhs):
        if self._varSigConst==varSig.runtime_variable_t:
            self._Connect_running_runtime_variable(rhs)
        elif gsimulation.isRunning():
            self._Connect_running(rhs)
        elif isFunction():
            pass
        else:
            self._Conect_Not_running(rhs)
            
    def __len__(self):
        return self.Bitwidth

    def __and__(self, rhs):
        if isinstance(rhs, v_symbol):
            bitShift = len(rhs)
            v  = value(self) << bitShift
            v += value(rhs)
            sl= slice_helper(start=0,stop=len(rhs)+len(self)-1)
            ret = v_slice_base(v,sl)
            return ret
        
        return rhs.l_append(self)

        


    def __int__(self):
        return value(self)


    def _issubclass_(self,test):
        if super()._issubclass_(test):
            return True
        return "v_symbol" == test












slv_includes = """
library IEEE;
library work;
  use IEEE.numeric_std.all;
  use IEEE.std_logic_1164.all;
  use ieee.std_logic_unsigned.all;
  use work.argg_hdl_core.all;
  use work.v_symbol_pack.all;
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
        Bitwidth=1,
        primitive_type ="boolean"
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
        Bitwidth=1,
        primitive_type ="std_logic"
    )

def v_slv(BitWidth=None,Default=0, Inout=InOut_t.Internal_t,varSigConst=None):


    alias = None
    value = Default
    if str(Default) == '0':
        Default = "(others => '0')"

    elif type(Default).__name__ == "int":
        Default = """std_logic_vector(to_unsigned({src}, {BitWidth}))""".format(
                src = Default,
                BitWidth=BitWidth
            )
    
    v_type = ""
    if BitWidth is None:
        v_type="std_logic_vector"  
        BitWidth=32  
    elif type(BitWidth).__name__ == "int":
        v_type="std_logic_vector(" + str(BitWidth -1 ) + " downto 0)"
        alias = "slv"+str(BitWidth)
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
        Bitwidth=int(BitWidth),
        primitive_type ="std_logic_vector",
        Alias = alias
    )

def v_int(Default=0, Inout=InOut_t.Internal_t, varSigConst=None,Bitwidth=32):
    
    return v_symbol(
        v_type= "integer",
        value= value(Default), 
        DefaultValue=str(Default), 
        Inout = Inout,
        includes=slv_includes,
        varSigConst=varSigConst,
        Bitwidth=Bitwidth,
        primitive_type ="integer"
    )

def v_uint(Default=0, Inout=InOut_t.Internal_t, varSigConst=None,Bitwidth=32):
    
    return v_symbol(
        v_type= "uinteger",
        value= value(Default), 
        DefaultValue=str(Default), 
        Inout = Inout,
        includes=slv_includes,
        varSigConst=varSigConst,
        Bitwidth=Bitwidth,
        primitive_type ="uinteger"
    )


def v_signed(BitWidth=None,Default=0, Inout=InOut_t.Internal_t, varSigConst=None):
    value = Default
    alias = None
    if str(Default) == '0':
        Default = "(others => '0')"

    elif type(Default).__name__ == "int":
        Default = """to_signed({src}, {BitWidth})""".format(
            src=Default,
            BitWidth=BitWidth
        )

    v_type = ""
    if BitWidth is None:
        v_type = "signed"
        BitWidth = 32
    elif type(BitWidth).__name__ == "int":
        v_type = "signed(" + str(BitWidth - 1) + " downto 0)"
        alias = "signed" + str(BitWidth)
    else:
        v_type = "signed(" + str(BitWidth) + " -1 downto 0)"
        BitWidth = 32

    return v_symbol(
        v_type=v_type,
        DefaultValue=Default,
        value=value,
        Inout=Inout,
        includes=slv_includes,
        varSigConst=varSigConst,
        Bitwidth=int(BitWidth),
        primitive_type="signed",
        Alias = alias
    )

def v_unsigned(BitWidth=None,Default=0, Inout=InOut_t.Internal_t, varSigConst=None):
    value = Default
    alias = None
    if str(Default) == '0':
        Default = "(others => '0')"

    elif type(Default).__name__ == "int":
        Default = """to_unsigned({src}, {BitWidth})""".format(
            src=Default,
            BitWidth=BitWidth
        )

    v_type = ""
    if BitWidth is None:
        v_type = "unsigned"
        BitWidth = 32
    elif type(BitWidth).__name__ == "int":
        v_type = "unsigned(" + str(BitWidth - 1) + " downto 0)"
        alias = "unsigned" + str(BitWidth)
    else:
        v_type = "unsigned(" + str(BitWidth) + " -1 downto 0)"
        BitWidth = 32

    return v_symbol(
        v_type=v_type,
        DefaultValue=Default,
        value=value,
        Inout=Inout,
        includes=slv_includes,
        varSigConst=varSigConst,
        Bitwidth=int(BitWidth),
        primitive_type="unsigned",
        Alias = alias
    )




@hdl_export()
def resize(symbol : v_symbol, newSize:int):
    ret =  v_symbol(
        v_type=symbol._type,
        DefaultValue=0,
        value=symbol,
        Inout=symbol._Inout,
        Bitwidth=newSize,
        primitive_type= symbol.primitive_type
    )

    symbol >> ret 
    return ret