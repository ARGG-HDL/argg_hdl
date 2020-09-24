import  functools 

import os,sys,inspect

from argg_hdl.argg_hdl_base import *
from argg_hdl.argg_hdl_v_symbol import *



class v_entity_list(argg_hdl_base0):
    def __init__(self):
        super().__init__()
        self.__hdl_converter__ = get_primitive_hdl_converter("v_entity_list" )()
        self.nexted_entities = list()


        self.__hdl_name__ = ""
        self._type = "v_entity_list"
        self.astParser = None
    
    def __or__(self,rhs):

        

        rhs_StreamIn = rhs._get_Stream_input()
        self_StreamOut = self._get_Stream_output()
        self.append(rhs)
        
        rhs_StreamIn << self_StreamOut
        
        return self
    
    def append(self, entity):
        if entity._issubclass_("v_symbol"):
            self.nexted_entities.append({
                "symbol" : entity,
                "temp"   : False
            })
        elif entity._issubclass_("v_class"):
            self.nexted_entities.append({
                "symbol" : entity,
                "temp"   : False
            })
        elif entity.__isInst__ == False:
            entity._instantiate_()
            self.nexted_entities.append({
                "symbol" : entity,
                "temp"   : True
            })
        else:
            self.nexted_entities.append({
                "symbol" : entity,
                "temp"   : False
            })


    def getMember(self,InOut_Filter=None, VaribleSignalFilter = None):
        ret = list()
        for x in self.nexted_entities:
            mem = x["symbol"].getMember(InOut_Filter, VaribleSignalFilter)
            ret += mem
        return ret

    def set_vhdl_name(self,name, Overwrite = False):
        if self.__hdl_name__ and self.__hdl_name__ != name and not Overwrite:
            raise Exception("double Conversion to vhdl")
        
        self.__hdl_name__ = name


    
    def set_simulation_param(self,module, name,writer):

        i = 0
        for x in self.nexted_entities:
            i+=1
            if x["temp"]:
                tempName =   name+"_"+str(i) + "_" +type(x["symbol"]).__name__
                x["symbol"].set_simulation_param(module, tempName,writer)

    


    def  __str__(self):
        ret = "----  --------- -------- " + self.__hdl_name__ +'----\n'
        return ret

    def _get_Stream_input(self):
        return self.nexted_entities[0]["symbol"]._get_Stream_output()


    def _get_Stream_output(self):
        return self.nexted_entities[-1]["symbol"]._get_Stream_output()


    def _issubclass_(self,test):
        if super()._issubclass_(test):
            return True
        return "v_entity_list" == test