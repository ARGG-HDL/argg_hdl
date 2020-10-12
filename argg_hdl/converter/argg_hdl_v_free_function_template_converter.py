import os
import sys
import inspect

from argg_hdl.argg_hdl__primitive_type_converter  import add_primitive_hdl_converter
from argg_hdl.argg_hdl_base import *
from argg_hdl.argg_hdl_v_function import *
import argg_hdl.argg_hdl_v_Package as argg_pack

class v_free_function_template_converter(hdl_converter_base):
    def __init__(self):
        super().__init__()
        self.__ast_functions__ = []

    def get_packet_file_name(self, obj):
        filename = obj.funcrec.filename.replace("\\","/").split("/")[-1].split(".")[0]
        funcName = obj.FuncName
        return filename + "_" + funcName + '.vhd'

    def get_packet_name(self,obj):
        filename = obj.funcrec.filename.replace("\\","/").split("/")[-1].split(".")[0]
        funcName = obj.FuncName
        PackageName = filename + "_" + funcName +"_pack"
        return PackageName

    def get_packet_file_content(self, obj):

        PackageName = self.get_packet_name(obj)
        s = isConverting2VHDL()
        set_isConverting2VHDL(True)


        pack  = argg_pack.v_package(PackageName,sourceFile=obj.__srcFilePath__,
            PackageContent = [
                obj
            ])

        fileContent = pack.to_string()
        set_isConverting2VHDL(s)
        return fileContent

    def def_packet_header(self, obj, name, parent):
        ret = ""
        
        for x in obj.__hdl_converter__.__ast_functions__:
            ret += hdl.def_packet_header(x, name,parent) +"\n"
        return ret
    
    
    def getBody(self, obj, name,parent):
        ret = ""
        
        for x in obj.__hdl_converter__.__ast_functions__:
            ret += hdl.getBody(x, name,parent) +"\n"
        return ret

    def includes(self,obj, name,parent):
        PackageName = self.get_packet_name(obj)
        ret = "use work." +  PackageName +".all;\n" 
        return ret


add_primitive_hdl_converter( v_free_function_template.__name__ , v_free_function_template_converter)