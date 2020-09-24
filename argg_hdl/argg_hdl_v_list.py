import os
import sys
import inspect
from typing import TypeVar, Generic

from argg_hdl.argg_hdl_base import *
from argg_hdl.argg_hdl_v_symbol import *

    
    

class v_list_slice(argg_hdl_base):
    def __init__(self,baseObject,slice_,content ):
        self.baseObject = baseObject
        self.l_append__ = []
        self.r_append__ = []
        self.slice = slice_
        self.content = content

    def r_append(self, rhs):
        self.r_append__ += [rhs]
        return self
    
    def l_append(self, lhs):
        self.l_append__ =[lhs] + self.l_append__
        return self

    def __len__(self):
        ret = 0
        for x in  self.l_append__:
            if isinstance(x, v_symbol):
                ret += 1
            else:
                ret += len(x)             
        
        ret += len(self.content)
        
        for x in  self.r_append__:
            if isinstance(x, v_symbol):
                ret += 1
            else:
                ret += len(x)             


        return ret

    def __getitem__(self,sl) -> T:
        if isinstance(sl, int):
            for x in  self.l_append__:
                if isinstance(x, v_symbol):
                    if sl == 0:
                        return x
                    sl  -= 1
                else:
                    raise Exception("not implemented yet")
                  
                    
            if  sl <  len( self.content):
                return self.content[sl ]
            sl -= len( self.content)

            
            for x in  self.r_append__:
                if isinstance(x, v_symbol):
                    if sl == 0:
                        return x
                    sl  -= 1
                else:
                    raise Exception("not implemented yet")
         
                
        
        return v_list_slice(self, sl ,self.content[value(sl)]) 

T = TypeVar('T')      
class v_list(argg_hdl_base, Generic[T]):
    def __init__(self,Internal_Type : T,size: int,varSigConst=None ):
        super().__init__()
        self.__hdl_converter__ =get_primitive_hdl_converter("v_list" )() 
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
        if isinstance(sl, slice):
            
            return v_list_slice(self, sl, self.content[value(sl)])
        
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
        if len(self.content) != len(rhs):
            raise Exception("Differnt list size")

        for x in range(len(self.content)):
            self.content[x] << rhs[x]

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

    def __iter__(self):
        return iter(self.content)

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
        
    def reset(self):
        for x in self.content:
            x.reset()

def call_func_v_list_reset(obj, name, args, astParser=None,func_args=None):
    asOp = args[0].__hdl_converter__.get_assiment_op(args[0])

    val = "(others => (others => '0'))"
    if val is None:
        raise Exception("unable to reset symbol")
    ret =  str(args[0])  + asOp + val
    args[0]._add_output()
    astParser.add_write(args[0])
    return ret