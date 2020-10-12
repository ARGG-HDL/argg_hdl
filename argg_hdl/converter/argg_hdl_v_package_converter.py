import ast
import os,sys,inspect


from argg_hdl.argg_hdl_base import *
from argg_hdl.argg_hdl_AST import xgenAST
from argg_hdl.argg_hdl_to_v_object import to_v_object
from argg_hdl.converter.argg_hdl_hdl_converter_base import hdl_converter_base
from argg_hdl.argg_hdl__primitive_type_converter  import add_primitive_hdl_converter

class v_package_converter(hdl_converter_base):
    def parse_file(self,obj):
        
        for t  in obj.PackageContent:
            t = to_v_object(t)
            
            t.__hdl_converter__.parse_file(t)


    def def_includes(self, obj, name,parent):
        #print(obj.PackageName)
        bufffer  = ""
        for t  in obj.PackageContent:
            t = to_v_object(t)
            bufffer += t.__hdl_converter__.def_includes(t,"",obj)
            dep_list = t.__hdl_converter__.get_dependency_objects(t,[])
            for y in dep_list:
                bufffer += y.__hdl_converter__.def_includes(y,"",obj)
        ret = make_unique_includes(bufffer, obj.PackageName)
        return ret

    def def_packet_header(self, obj, name,parent):
        ret = ""
        for t  in obj.PackageContent:
            t = to_v_object(t)
            ret += t.__hdl_converter__.def_packet_header(t,"",obj)
        
        return ret

    def def_packet_body(self,obj, name,parent):
        ret = ""
        for t  in obj.PackageContent:
            t = to_v_object(t)
            ret += t.__hdl_converter__.def_packet_body(t,"",obj)
        
        return ret



def make_inque_list(list_in):
    uniqueList = []
    for ele in list_in:
        if ele not in uniqueList:
            uniqueList.append(ele)
    return uniqueList




add_primitive_hdl_converter("v_package",v_package_converter )
