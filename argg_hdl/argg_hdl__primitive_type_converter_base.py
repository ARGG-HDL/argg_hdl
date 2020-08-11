
from argg_hdl.argg_hdl_base import *
from argg_hdl.argg_hdl__primitive_type_converter  import add_primitive_hdl_converter


from argg_hdl.argg_hdl_v_symbol import *


class v_symbol_converter(hdl_converter_base):

    primitive_type = "base"
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
        if obj.__isFreeType__:
            return []

        if parent._issubclass_("v_class"):
            return name + " : " +obj._type

        return []

    def recordMemberDefault(self, obj,name,parent,Inout=None):
        if obj.__isFreeType__:
            return []
        
        if parent._issubclass_("v_class"):
            return name + " => " + obj.DefaultValue 

        return []

    def getHeader(self, obj,name,parent):
        if obj.__hdl_name__:
            name = obj.__hdl_name__

        if parent._issubclass_("v_class"):
             return ""
            
        return name + " : " +obj._type +" := " +  obj.DefaultValue  + "; \n"

    def getFuncArg(self,obj, name,parent):
        return name + " : " + obj._type   

    def _vhdl_slice(self,obj,sl,astParser=None):
        raise Exception("unexpected type")


    def _vhdl__compare_int(self,obj, ops, rhs):
        return str(obj) + " "+ obj.__hdl_converter__.ops2str(ops) +" " +   str(rhs)


    

    def _vhdl__compare(self,obj, ops, rhs, astParser):
        astParser.add_read(obj)
        obj._add_input()
        if issubclass(type(rhs),argg_hdl_base):
            astParser.add_read(rhs)
            rhs._add_input()
    
        if obj._type == "integer":
            return obj.__hdl_converter__._vhdl__compare_int(obj, ops, rhs)
        
        
        return str(obj) + " "+ obj.__hdl_converter__.ops2str(ops)+" " +   str(rhs)

    def _to_hdl___bool__(self,obj:v_symbol, astParser):
        obj._add_input()
        astParser.add_read(obj)

        if obj._type == "boolean":
            return str(obj)

        return "to_bool(" + str(obj) + ") "

    def _vhdl__BitAnd(self,obj:"v_symbol",rhs,astParser) -> "v_symbol":
        ret = v_slv()
        ret.set_vhdl_name(str(obj)+ " & " +str(rhs) ,True)
        return ret


    def _vhdl__DefineSymbol(self,obj:"v_symbol", VarSymb=None):
        print_cnvt("_vhdl__DefineSymbol is deprecated")
        if not VarSymb:
            VarSymb = get_varSig(obj._varSigConst)

        if  obj.__Driver__ is not None and str(obj.__Driver__ ) != 'process' and str(obj.__Driver__ ) != 'function':
            return ""
        name = obj.__hdl_name__

        ty = str(value(obj.primitive_type)) + "("+str(obj.Bitwidth_raw) +" - 1 downto 0)"
        default_value = self.get_default_value(obj)

        return  VarSymb+ " " + str(name) + " : " + ty +" := " +  default_value  + "; \n"
    def get_architecture_header(self, obj):

        if obj._Inout != InOut_t.Internal_t and not obj.__isInst__:
            return ""
        
        if obj._varSigConst == varSig.variable_t:
            return ""
        
        
        VarSymb = get_varSig(obj._varSigConst)

        #if  obj.__Driver__ != None and str(obj.__Driver__ ) != 'process':
        #    return ""
        name = obj.__hdl_name__
        default_value = self.get_default_value(obj)
        ret = "  " + VarSymb+ " " + name + " : " +obj._type +" := " + default_value + "; \n"   
        return  ret

    def get_port_list(self,obj:"v_symbol"):
        ret = []
        if obj._Inout == InOut_t.Internal_t:
            return ret
        
        if obj._varSigConst != varSig.signal_t:
            return ret
        
        ret.append( obj.__hdl_name__ + " : "+ obj.__hdl_converter__.InOut_t2str(obj) + " " + obj._type + " := " + obj.DefaultValue)
        return ret





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

        asOp = obj.__hdl_converter__.get_assiment_op(obj)            
        return target +asOp +  str(rhs)
    


    def _vhdl__reasign_rshift_(self, obj, rhs, astParser=None,context_str=None):
        return hdl._vhdl__reasign(rhs, obj,astParser,context_str)

    def get_type_simple(self,obj:"v_symbol"):
        return obj._type

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
        inout = astParser.get_function_arg_inout_type(obj)
        inoutstr = obj.__hdl_converter__.InOut_t2str(obj)
        varSigstr = ""
        if obj._varSigConst == varSig.signal_t:
            varSigstr = "signal "

        if not inoutstr:
            inoutstr = ""
        default_str = ""
        if withDefault and obj.__writeRead__ != InOut_t.output_t and obj._Inout != InOut_t.output_t:
            default_str =  " := " + str(obj.__hdl_converter__.get_default_value(obj))

        return varSigstr + name + " : " + inoutstr +" " + obj.__hdl_converter__.get_type_func_arg(obj) + default_str
    
    def get_free_symbols(self,obj,parent_list=[]):
        if obj.__isFreeType__:
            return [obj]
        
        return []


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