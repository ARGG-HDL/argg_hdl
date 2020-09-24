import  functools 

import os,sys,inspect

from argg_hdl.argg_hdl_base import *
from argg_hdl.argg_hdl_v_symbol import *

from argg_hdl.argg_hdl__primitive_type_converter  import add_primitive_hdl_converter
from argg_hdl.converter.argg_hdl_hdl_converter_base import hdl_converter_base



class v_entity_list_converter(hdl_converter_base):
        def __init__(self):
            super().__init__()
        def get_architecture_header(self, obj):
            ret = "--------------------------"+ obj.__hdl_name__  +"-----------------\n"
            VarSymb = "signal"
            i = 0
            for x in obj.nexted_entities:
                i+=1
                if x["symbol"].__hdl_name__ is None or x["temp"]:
                    x["temp"] = True
                    tempName = obj.__hdl_name__ +"_"+ str(i) + "_" +type(x["symbol"]).__name__
                    x["symbol"].set_vhdl_name(tempName)
                    ret += x["symbol"].__hdl_converter__.get_architecture_header(x["symbol"])
            ret += "-------------------------- end "+ obj.__hdl_name__  +"-----------------\n"
            return ret


        def get_architecture_body(self, obj):
            
            ret = ""
            i = 0
            start = ""
            for x in obj.nexted_entities:
                i+=1
                if  x["symbol"].__hdl_name__ is None or x["temp"]:
                    x["temp"] = True
                    tempName = str(obj.__hdl_name__) +"_"+  str(i) + "_" +type(x["symbol"]).__name__
                    if not x["symbol"].__hdl_name__:
                        x["symbol"].set_vhdl_name(tempName)
                    ret += start + x["symbol"].__hdl_converter__.get_architecture_body(x["symbol"])
                    start = ";\n  "
            


            return ret

        def includes(self,obj, name,parent):
            bufffer = ""
            
            for x in obj.nexted_entities:
                bufffer += x["symbol"].__hdl_converter__.includes(x["symbol"], None, None)

            ret  = make_unique_includes(bufffer)

            return ret

add_primitive_hdl_converter("v_entity_list" ,v_entity_list_converter)