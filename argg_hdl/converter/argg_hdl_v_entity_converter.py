from argg_hdl.argg_hdl__primitive_type_converter  import add_primitive_hdl_converter
from  argg_hdl.argg_hdl_object_name_maker import  make_object_name
import  argg_hdl.argg_hdl_hdl_converter as  hdl
from argg_hdl.argg_hdl_base import *
from argg_hdl.argg_hdl_v_symbol import *
from argg_hdl.argg_hdl_v_entity_list import *
from argg_hdl.argg_hdl_AST import *
from argg_hdl.argg_hdl_v_entity import *


class v_entity_converter(hdl_converter_base):
    def __init__(self):
        super().__init__()
        self.astTree = None

    def get_type_simple(self,obj):

        objTypeName = type(obj).__name__

        MemberTypeNames = [
            hdl.get_type_simple_template(x["symbol"])
            for x in obj.getMember()
        ]

        ret = make_object_name(objTypeName,MemberTypeNames)
        return ret 

    def get_entity_file_name(self, obj):
        type_name  = self.get_type_simple(obj)
        return type_name+".vhd"

    def get_enity_file_content(self, obj):
        s = isConverting2VHDL()
        set_isConverting2VHDL(True)
        hdl_name = obj.__hdl_name__
        obj._un_instantiate_()
        obj.__hdl_converter__.MissingTemplate = False
        obj.__processList__ = []
        
        astparser = obj.__hdl_converter__.parse_file(obj)
        
        ret = "-- XGEN: Autogenerated File\n\n"
        ret += obj.__hdl_converter__.def_includes(obj, None, obj)
        ret += "\n\n"
        
        ret += obj.__hdl_converter__.get_definition(obj)
        
        if astparser.Missing_template:
                obj.__hdl_converter__.FlagFor_TemplateMissing(obj)
                obj.__hdl_converter__.MissingTemplate = True
                print_cnvt(str(gTemplateIndent)+'<Failed_to_convert name="' + type(obj).__name__ +'"/>')

        obj._instantiate_()
        if hdl_name:
            obj.set_vhdl_name(hdl_name , True)
        set_isConverting2VHDL(s)
        return ret




    def parse_file(self,obj):
        if obj.__srcFilePath__:
            self.astTree = xgenAST(obj.__srcFilePath__)
            self.astTree.extractArchetectureForEntity(obj,None)
            return self.astTree

        
    def impl_get_attribute(self,obj, attName,parent=None):
        if obj.__hdl_name__:
            return obj.__hdl_name__ +"_"+ attName
        
        return attName

    def get_archhitecture(self,obj):
        type_name  = self.get_type_simple(obj)
        ret = "architecture rtl of "+ type_name +" is\n\n"

        ret +=  obj.__hdl_converter__.impl_architecture_header_def(obj)
        ret += "\nbegin\n"
        ret +=  obj.__hdl_converter__.impl_architecture_body_def(obj)
        ret += "\nend architecture;\n"
        ret = hdl_string_fix_semicolons(ret)
        return ret 

    def impl_architecture_header_def(self, obj):
        if obj.__hdl_name__:
            name = obj.__hdl_name__
        else :
            name = obj._name
        ret = "--------------------------"+ name  +"-----------------\n"
        members= obj.__hdl_converter__.getMember(obj)
        
        for x in members:
            sym = x["symbol"]
            symName = obj.__hdl_converter__.impl_get_attribute(obj,x["name"])
            sym.__hdl_name__ = symName
            
            ret +=  sym.__hdl_converter__.impl_architecture_header(sym)


        for x in obj.__processList__:
            ret += x.__hdl_converter__.impl_architecture_header(x)

        ret += "-------------------------- end "+ name  +"-----------------\n"
        return ret 


    def impl_architecture_header(self, obj):
        if obj.__hdl_name__:
            name = obj.__hdl_name__
        else :
            name = obj._name
        ret = "--------------------------"+ name  +"-----------------\n"
        members= obj.__hdl_converter__.getMember(obj)
        
        for x in members:
            sym = x["symbol"]
            if sym._Inout ==InOut_t.Internal_t:
                continue
            symName = obj.__hdl_converter__.impl_get_attribute(obj,x["name"])
            sym.set_vhdl_name( symName,True)
            
            ret +=  hdl.impl_architecture_header(sym)

        ret += "-------------------------- end "+ name  +"-----------------\n"
        return ret 


    def impl_architecture_body(self, obj):
        type_name  = self.get_type_simple(obj)
        content = []

        for x in v_entity_getMember(obj):
            if x["symbol"]._Inout ==InOut_t.Internal_t:
                continue
            if not x["symbol"].__hdl_name__:
                x["symbol"].set_vhdl_name(str(obj.__hdl_name__)+"_"+ x["name"])

            content += x["symbol"].__hdl_converter__.impl_entity_port(x["symbol"], x["name"] )


        start = str(obj.__hdl_name__) +" : entity work." + type_name +" port map (\n    "
        ret=join_str(content,start=start ,end="\n  )",Delimeter=",\n    ")
        return ret
 

    def impl_architecture_body_def(self, obj):
        ret = ""
        for x in obj.__processList__:
            x.isEntity = True
            ret += x.__hdl_converter__.impl_architecture_body(x)
        return ret 



    def getMember(self, obj):
        return v_entity_getMember(obj)
    
    def def_includes(self,obj, name,parent):
        bufffer = ""
        members= obj.__hdl_converter__.getMember(obj)
        for x in members:
            bufffer += x["symbol"].__hdl_converter__.def_includes(x["symbol"],x["name"],None)

        for x in obj.__processList__:
            bufffer += x.__hdl_converter__.def_includes(x,"",None)


        ret = make_unique_includes(bufffer)
        return ret

    def get_declaration(self,obj):
        type_name  = self.get_type_simple(obj)
        portdef=[]
        
        for x in obj.__hdl_converter__.getMember(obj):
            sym = x["symbol"]
            sym.__hdl_name__ = x["name"]
            portdef += hdl.def_entity_port(sym)

      
        ret = "entity " + type_name + " is \n" 
        ret+=join_str(portdef,start="  port(\n    " ,end="\n  );\n",Delimeter=";\n    ",IgnoreIfEmpty=True)
        ret += "end entity;\n\n"
        return ret

    def get_definition(self, obj):
    
        if obj.__isInst__:
            obj._un_instantiate_()
        ret = ""

        ret += "\n\n"
        ret += obj.__hdl_converter__.get_declaration(obj)
        ret += "\n\n"
        ret += obj.__hdl_converter__.get_archhitecture(obj)
        ret = ret.strip()
        return ret

    def get_process_header(self,obj):
        return ""
        




add_primitive_hdl_converter("v_entity",v_entity_converter )
