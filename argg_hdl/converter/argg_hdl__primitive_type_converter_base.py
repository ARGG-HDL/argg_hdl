
from argg_hdl.argg_hdl_base import *
from argg_hdl.argg_hdl__primitive_type_converter  import add_primitive_hdl_converter


from argg_hdl.argg_hdl_v_symbol import *

from  argg_hdl.free_type_helper import extracted_freeType
from argg_hdl.converter.argg_hdl_hdl_converter_base import hdl_converter_base
class v_symbol_type_alias:
    def __init__(self, obj,alias):
        self.obj = obj
        self.alias = alias


class v_symbol_converter(hdl_converter_base):

    defined_types = []
    primitive_type = "base"

    def add_alias(self,obj,alias_name):
        self.defined_types.append(v_symbol_type_alias(obj , alias_name))
        self.AliasType = alias_name

    def __init__(self,inc_str):
        super().__init__()
        self.inc_str  = inc_str
        self.AliasType = None
        self.extractedTypes = []

    def make_constant(self, obj:"v_symbol", name,parent=None,InOut_Filter=None, VaribleSignalFilter = None):
        return ""
        
    def prepare_for_conversion(self,obj:"v_symbol"):
        
        
        if not obj.__hdl_converter__.extractedTypes:
            obj.__hdl_converter__.extractedTypes += [v_copy(obj)]

        for m in obj.__dict__:
            if not issubclass(type(m),argg_hdl_base0):
                continue 
            hdl.prepare_for_conversion(m)
    
    def get_packet_file_name(self, obj:"v_symbol"):
        return "v_symbol_pack.vhd"

    def get_packet_file_content(self, obj:"v_symbol"):
        
        includes = ""
        header = "" 
        body = ""
        aliases = []
        for x in self.defined_types:
            if x.alias is None:
                continue
            if x.alias in aliases:
                continue
            
            aliases.append(x.alias)

            
            
            
            


            subtype_def       = "    subtype " +x.alias  + " is " + x.obj._type +";\n"
            null_const        = "    constant " + x.alias+"_null : " + x.alias +" := " +x.obj.DefaultValue +";\n"
            array_of_subtype  = "    type "+x.alias+"_a is array (natural range <>) of " + x.alias + ";\n"
            func_declaration  = "    function "+x.alias+"_ctr(Data : Integer) return " + x.alias+";\n"
            func_definition   = """
    function {alias}_ctr(Data : Integer) return  {alias} is 
    variable ret : {alias};
    begin
        ret := {base_type}_ctr(Data , {alias}'length);
        return ret;
    end function;     

            """.format(
                alias = x.alias,
                base_type =x.obj.primitive_type 
            )

            header += subtype_def +null_const +array_of_subtype+ func_declaration +"\n\n"
            body += func_definition 
            includes += hdl.includes(obj,"", None)


        includes = make_unique_includes(includes, "v_symbol_pack")

        ret = includes+ "\n\n\npackage v_symbol_pack is \n\n " + header  +   "\n\nend package;\n\npackage body v_symbol_pack is\n\n" + body +"\nend package body;\n"
        return ret

    def get_dependency_objects(self, obj:"v_symbol", depList):
        return obj
        
    def includes(self,obj, name,parent):
        ret = slv_includes
        ret += self.inc_str
        return ret


    def _vhdl__call_member_func(self, obj:"v_symbol", name, args, astParser=None):
        
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

    def get_get_call_member_function(self, obj:"v_symbol", name, args):
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
        
    def def_record_Member(self,obj:"v_symbol", name, parent,Inout=None):
        if obj.__isFreeType__:
            return []


        return name + " : " + hdl.get_type_simple(obj)



    def def_record_Member_Default(self, obj:"v_symbol",name,parent,Inout=None):
        if obj.__isFreeType__:
            return []
        

        return name + " => " + hdl.impl_constructor(obj)



    def def_packet_header(self, obj:"v_symbol",name,parent):
        if obj.__hdl_name__:
            name = obj.__hdl_name__

        if parent._issubclass_("v_class"):
             return ""
            
        return name + " : " +obj._type +" := " +  hdl.impl_constructor(obj) + "; \n"



    def impl_slice(self,obj:"v_symbol",sl,astParser=None):
        raise Exception("unexpected type")





    

    def impl_compare(self,obj:"v_symbol", ops, rhs, astParser):
        astParser.add_read(obj)
        obj._add_input()
        if issubclass(type(rhs),argg_hdl_base):
            astParser.add_read(rhs)
            rhs._add_input()
    

        
        
        return str(obj) + " "+ obj.__hdl_converter__.ops2str(ops)+" " +   str(rhs)



    def impl_bit_and(self,obj:"v_symbol",rhs,astParser) -> "v_symbol":
        ret = v_slv()
        ret.set_vhdl_name(str(obj)+ " & " +str(rhs) ,True)
        return ret


    def impl_symbol_instantiation(self,obj:"v_symbol", VarSymb=None):
        print_cnvt("impl_symbol_instantiation is deprecated")
        if not VarSymb:
            VarSymb = get_varSig(obj._varSigConst)

        if  obj.__Driver__ is not None and str(obj.__Driver__ ) != 'process' and str(obj.__Driver__ ) != 'function':
            return ""


        return  VarSymb+ " " + str(obj.__hdl_name__) + " : " + hdl.get_type_simple(obj) +" := " +  hdl.impl_constructor(obj) + "; \n"    
    
    def impl_architecture_header(self, obj:"v_symbol"):

        if obj._Inout != InOut_t.Internal_t and not obj.__isInst__:
            return ""
        
        if obj._varSigConst == varSig.variable_t:
            return ""

        if obj.__isFreeType__ and obj._Inout == InOut_t.output_t:
            return ""
        VarSymb = get_varSig(obj._varSigConst)
        ret = "  " +VarSymb + " " + str( obj.__hdl_name__) + " : " + hdl.get_type_simple(obj) +" := " + hdl.impl_constructor(obj) + "; \n"   
        return  ret

    def def_entity_port(self,obj:"v_symbol"):
        if obj._Inout == InOut_t.Internal_t:
            return []
        
        if obj._varSigConst != varSig.signal_t:
            return []
        
        return [
            obj.__hdl_name__ + 
            " : "+ 
            obj.__hdl_converter__.InOut_t2str(obj) + 
            " " +  
            hdl.get_type_simple(obj) + 
            " := " + 
            hdl.impl_constructor(obj)]
        





    def impl_reasign(self, obj:"v_symbol", rhs, astParser=None,context_str=None):
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

        asOp = obj.__hdl_converter__.get_assiment_op(obj)            
        return target +asOp +  str(rhs)
    


    def impl_reasign_rshift_(self, obj:"v_symbol", rhs, astParser=None,context_str=None):
        return hdl.impl_reasign(rhs, obj,astParser,context_str)

    def get_type_simple(self,obj:"v_symbol"):
        return obj._type
    
    def get_type_simple_template(self,obj:"v_symbol"):
        if obj._varSigConst == varSig.const_t:
            return "c_" + obj._type + "_" + str(value(obj))
        return obj._type
    
    def impl_constructor(self,obj):
        return obj.primitive_type+"_ctr(" +str(value(obj))+ ", " + str(obj.Bitwidth_raw) + ")"
    
    def impl_get_value(self,obj:"v_symbol", ReturnToObj=None,astParser=None):
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

        return obj

    def get_default_value(self,obj:"v_symbol"):
        return obj.DefaultValue

    def length(self,obj:"v_symbol"):
        ret = v_int()
        ret.__hdl_name__=str(obj)+"'length"
        return ret

    def get_type_func_arg(self,obj:"v_symbol"):
        ret = obj.get_type()
        return ret


    def to_arglist(self,obj:"v_symbol", name,parent,withDefault = False,astParser=None):
        inoutstr =""
        if astParser:
            inout = astParser.get_function_arg_inout_type(obj)
            inoutstr = obj.__hdl_converter__.InOut_t2str2(inout)
        
        varSigstr = ""
        if obj._varSigConst == varSig.signal_t:
            varSigstr = "signal "

        if not inoutstr:
            inoutstr = ""
        default_str = ""
        if withDefault and obj.__writeRead__ != InOut_t.output_t and obj._Inout != InOut_t.output_t:
            default_str =  " := " + str(obj.__hdl_converter__.get_default_value(obj))

        return varSigstr + name + " : " + inoutstr +" " + obj.__hdl_converter__.get_type_func_arg(obj) + default_str
    
    def get_free_symbols(self,obj:"v_symbol",name, parent_list=[]):
        if obj.__isFreeType__:
            suffix = join_str([x["name"] for x in parent_list],Delimeter="_",end="_"+name)
            ret = extracted_freeType(obj, suffix)
            return [ret]
        
        return []
    
    def get_init_values(self,obj:"v_symbol", parent=None, InOut_Filter=None, VaribleSignalFilter = None,ForceExpand=False):
        ret =  hdl.impl_constructor(obj)
        return ret



slv_includes = """
library IEEE;
library work;
  use IEEE.numeric_std.all;
  use IEEE.std_logic_1164.all;
  use ieee.std_logic_unsigned.all;
  use work.argg_hdl_core.all;
"""



def call_func_symb_reset(obj, name, args, astParser=None,func_args=None):
    asOp = args[0].__hdl_converter__.get_assiment_op(args[0])
    val = None
    if obj._type == "std_logic":
        val = "'0'"
    if "std_logic_vector" in obj._type:
        val = "(others => '0')"
    if obj._type == "integer":
        val = '0'
    
    if "signed" in obj._type:
        val = "(others => '0')"
    
    if val is None:
        raise Exception("unable to reset symbol")
    ret =  str(args[0])  + asOp + val
    args[0]._add_output()
    astParser.add_write(args[0])
    return ret



add_primitive_hdl_converter("base",v_symbol_converter )


def reset_v_symbols():
    v_symbol_converter.defined_types = []

g_add_global_reset_function(reset_v_symbols)
