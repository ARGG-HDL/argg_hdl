import  functools 

import os
import sys
import inspect

from argg_hdl.argg_hdl_base import *
from argg_hdl.argg_hdl_v_symbol import *
from argg_hdl.argg_hdl_v_entity_list import *
from argg_hdl.argg_hdl_AST import *
from argg_hdl.argg_hdl_object_factory import add_constructor

from typing import Sequence, TypeVar
T = TypeVar('T', bound='Copyable')





def process():
    def decorator_processd(func):
        @functools.wraps(func)
        def wrapper_process(getSymb=None):
            return func()
        localVarSig = getDefaultVarSig()

        setDefaultVarSig(varSig.variable_t)
        func()
        setDefaultVarSig(localVarSig)
        add_symbols_to_entiy()

        return wrapper_process
    return decorator_processd



def timed():
    def decorator_timed(func):
        @functools.wraps(func)
        def wrapper_timed(getSymb=None):
            return func()

        gsimulation.timmed_process.append(func)
        return wrapper_timed
    return decorator_timed

def v_create(entity : T) -> T:
    entity._instantiate_()
    return entity

class wait_for():
    def __init__(self,time,unit="ns"):
        self.time =time 
        self.unit = unit

    def get_time(self):
        return self.time

    def __str__(self):
        return " " + str(self.time) +" " + self.unit



            
def addPullsPushes_from_closure(Pull_list, Push_list, closure):
    if closure is None:
        return
    for x in closure:
        y = x.cell_contents
        if issubclass(type(y), argg_hdl_base0):
            y._sim_set_push_pull(Pull_list, Push_list)
            



def combinational():
    def decorator_combinational(func):
        @functools.wraps(func)
        def wrapper_combinational():
            return func()

        for symb in func.__closure__:
            symbol = symb.cell_contents
            symbol._sim_append_update_list(wrapper_combinational)
        return wrapper_combinational
    return decorator_combinational

def v_switch(default_value, v_cases):
    for c in v_cases:
        if c["pred"]:
            return c["value"]

    return default_value

def v_case(pred,value):
    ret = {
        "pred" : pred,
        "value" : value 
    }
    return ret

def run_list(functionList):
    for x in functionList:
        x()


def rising_edge(symbol):
    def decorator_rising_edge(func):
        Pull_list = []
        Push_list = []
        @functools.wraps(func)
        def wrapper_rising_edge(getSymb=None):
            if value(symbol) == 1:
                run_list(Pull_list)
                func()
                run_list(Push_list)

        
        addPullsPushes_from_closure(Pull_list,Push_list ,func.__closure__)
        symbol.__update__list_process__.append(wrapper_rising_edge)
        return wrapper_rising_edge
    return decorator_rising_edge

gport_veto__ =[
            "_StreamOut",
            "_StreamIn"
        ]

def v_entity_getMember(entity):
        ret = list()
        for x in entity.__dict__.items():
            if x[0] in gport_veto__:
                continue

            t = getattr(entity, x[0])
            if issubclass(type(t),argg_hdl_base):
                ret.append({
                        "name": x[0],
                        "symbol": t
                    })

        ret=sorted(ret, key=lambda element_: element_["name"])
        return ret

def v_entity_getMember_expand(entity):
        ret = list()
        for x in entity.__dict__.items():
            if x in gport_veto__:
                continue
            t = getattr(entity, x[0])
            if t._issubclass_("v_class"):
                ret.append({
                        "name": x[0],
                        "symbol": t
                    })
            elif t._issubclass_("argg_hdl_base"):
                ret.append({
                        "name": x[0],
                        "symbol": t
                    })
        
        ret=sorted(ret, key=lambda element_: element_["name"])
        return ret

        


class InstantiateAfterInit(type):
    def __call__(cls, *args, **kwargs):
        """Called when you call MyNewClass() """
        obj = type.__call__(cls, *args, **kwargs)
        obj._instantiate_()
        return obj

class v_entity(argg_hdl_base0, metaclass=InstantiateAfterInit):
    def __init__(self):
        super().__init__()

        self.__hdl_converter__= get_primitive_hdl_converter("v_entity" )()
        setDefaultVarSig(varSig.signal_t)
        name = type(self).__name__
        self._name = name
        #self.__srcFilePath__ = srcFileName
        self.__processList__ = list()
        self._Inout = InOut_t.Internal_t
        self.__hdl_name__ = None
        self._type = "entity"
        self.__local_symbols__ = list()
        self._StreamOut = None
        self._StreamIn  = None

    def get_clk(self):
        raise Exception("no Clock Defined for this entity", self)
        
    def getMember(self,InOut_Filter=None, VaribleSignalFilter = None):
        ret = list()
        for x in self.__dict__.items():
            t = getattr(self, x[0])
            if not issubclass(type(t),argg_hdl_base) :
                continue 
            if not t.isInOutType(InOut_Filter):
                continue
            
            if not t.isVarSigType(VaribleSignalFilter):
                continue

            ret.append({
                        "name": x[0],
                        "symbol": t
                    })

        ret =sorted(ret, key=lambda element_: element_["name"])
        return ret


    def __or__(self,rhs):

        
        rhs_StreamIn = rhs._get_Stream_input()
        self_StreamOut = self._get_Stream_output()
                
        ret = v_entity_list()


        ret.append(self)
        ret.append(rhs)

        rhs_StreamIn << self_StreamOut
        return ret
        
    def set_simulation_param(self,module, name,writer):
        mem = v_entity_getMember(self)
        for x in mem:
            x["symbol"].set_simulation_param(module +"."+ name, x["name"],writer)

        local_symbols =sorted(self.__local_symbols__, key=lambda element_: element_["name"])
        for x in local_symbols:
            x["symbol"].set_simulation_param(module +"."+ name, x["name"],writer)


    def _add_symbol(self, name,symb):
        for x in self.__local_symbols__:
            if symb is x["symbol"]:
                return

        type_name = name
        if issubclass(type(symb), v_entity):
            type_name = "zzzzzzz_"+ name
            
        self.__local_symbols__.append(
            {
                "name" : name,
                "symbol" : symb,
                "type_name" : type_name
            }
        )


    def _instantiate_(self):
        if self.__isInst__:
            return self
            
        mem = v_entity_getMember(self)
        for x in mem:
            self.__dict__[x["name"]]._instantiate_()
        
        self.__isInst__ = True
        return self

    def _un_instantiate_(self, Name = ""):
        if not self.__isInst__:
            return self
        

        self.set_vhdl_name(Name, True)
        mem = v_entity_getMember(self)
        for x in mem:
            self.__dict__[x["name"]]._un_instantiate_(x["name"])

        
        self.__isInst__ = False
        return self



    def _sim_append_update_list(self,up):
        pass

    def set_vhdl_name(self,name, Overwrite = False):
        if self.__hdl_name__ and self.__hdl_name__ != name and not Overwrite:
            raise Exception("double Conversion to vhdl")

        self.__hdl_name__ = name
        
        mem = v_entity_getMember(self)
        for x in mem:
            self.__dict__[x["name"]].set_vhdl_name(name+"_"+x["name"], Overwrite)



    def _get_Stream_input(self):
        if self._StreamIn is None:
            raise Exception("Input stream not defined")
        return  self._StreamIn

    def _get_Stream_output(self):
        if self._StreamOut is None:
            raise Exception("output stream not defined")
        return self._StreamOut


    def _issubclass_(self,test):
        if super()._issubclass_(test):
            return True
        return "v_entity" == test

def clock_t():
    clk   =  v_sl() 
    clk.__isFreeType__ = True
    return clk 

class v_clk_entity(v_entity):
    def __init__(self,clk=None):
        super().__init__()
        self.clk    =  port_in(clock_t())
        if clk is not  None:
            self.clk <<  clk
    
    def get_clk(self):
        return self.clk

    def _issubclass_(self,test):
        if super()._issubclass_(test):
            return True
        return "v_clk_entity" == test



add_constructor("v_clk_entity",v_clk_entity)
add_constructor("v_entity",v_entity)