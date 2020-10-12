
import copy


import os
import sys
import inspect

from argg_hdl.argg_hdl_base import *
from argg_hdl.argg_hdl_v_enum import * 
from argg_hdl.argg_hdl_to_v_object import *
from argg_hdl.argg_hdl_v_symbol  import *
from argg_hdl.argg_hdl_v_function  import v_free_function_template
import  argg_hdl.argg_hdl_hdl_converter as  hdl
from argg_hdl.ast.argg_hdl_ast_hdl_error import argg_hdl_error

def Node_line_col_2_str(astParser, Node):
    return  "Error in File: "+ astParser.sourceFileName+" line: "+str(Node.lineno) + ".\n"


def unfold_Str(astParser, strNode):
    return strNode.s
def unfold_num(astParser, NumNode):
    return NumNode.n


def Unfold_call(astParser, callNode):
        
    return astParser._unfold_symbol_fun_arg[callNode.func.id](astParser, callNode.args)


def isDecoratorName(dec, Name):
    if len(dec) == 0:
        return False
    if hasattr(dec[0], "func"): 
        if hasattr(dec[0].func, "id"):
            return dec[0].func.id== Name
    if hasattr(dec[0], "id"):
        return dec[0].id== Name
    return False
    


class GNames:
    process = "process"



gIndent = indent()


def port_in_to_vhdl(astParser,Node,Keywords=None):
    return port_in(astParser.unfold_argList(Node[0]) )

def port_out_to_vhdl(astParser,Node,Keywords=None):
    return port_out(astParser.unfold_argList(Node[0]) )

def variable_port_in_to_vhdl(astParser,Node,Keywords=None):
    return variable_port_in(astParser.unfold_argList(Node[0]) )

def variable_port_out_to_vhdl(astParser,Node,Keywords=None):
    return  variable_port_out(astParser.unfold_argList(Node[0]) )

def v_symbol_to_vhdl(astParser,Node,Keywords=None):
    args = list()
    for x in Node:
        x_obj = astParser.Unfold_body(x)
        if type(x_obj).__name__ == "v_Num":
            args.append(x_obj.value )
        else:
            args.append(x_obj)

    kwargs = {}
    if Keywords:
        for x in Keywords:
            if x.arg =='varSigConst':
                temp = astParser.Unfold_body(x.value).Value 
                temp._add_input()
                kwargs[x.arg] = temp
            else:
                temp = astParser.Unfold_body(x.value) 
                temp._add_input()
                kwargs[x.arg] = temp

    return v_symbol(*args,**kwargs)  


def v_slv_to_vhdl(astParser,Node,Keywords=None):
    args = list()
    for x in Node:
        x_obj = astParser.Unfold_body(x)
        if type(x_obj).__name__ == "v_Num":
            args.append(x_obj.value )
        else:
            args.append(x_obj)

    kwargs = {}
    if Keywords:
        for x in Keywords:
            if x.arg =='varSigConst':
                kwargs[x.arg] = astParser.Unfold_body(x.value).Value 
            else:
                kwargs[x.arg] = astParser.Unfold_body(x.value) 

    return v_slv(*args,**kwargs)


def v_sl_to_vhdl(astParser,Node,Keywords=None):
    if len(Node) == 1:
        return v_sl(InOut_t.input_t, astParser.unfold_argList(Node[0]) )
    
    return v_sl(InOut_t.input_t )
        
        
def v_int_to_vhdl(astParser,Node,Keywords=None):
    return v_int()


def v_bool_to_vhdl(astParser,Node,Keywords=None):
    return v_bool()
class v_ast_base:

    def __str__(self):
        return type(self).__name__

    def get_type(self):
        return ""
        
    def impl_get_value(self,ReturnToObj=None,astParser=None):
        self._vhdl__setReturnType(ReturnToObj, astParser)
        return str(self)    

    def _vhdl__setReturnType(self,ReturnToObj=None,astParser=None):
        pass

    def get_symbol(self):
        return None

class v_noop(v_ast_base):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):

        return ""

class v_process_Def(v_ast_base):
    def __init__(self,BodyList,name,dec=None):
        self.BodyList=BodyList
        self.dec = dec
        self.name = name
    
    def __str__(self):
        ret = "\n-----------------------------------\n" + self.name + " : process" 
        for x in self.BodyList:
            x_str =str(x) 
            sp_x_str = x_str.split("\n")[-1].strip()
            if x_str:
                x_str = x_str.replace("\n", "\n  ")
                ret += x_str
                if sp_x_str:
                    ret += ";"
                ret += "\n  "  

        ret += "end process"
        return ret

def body_unfold_porcess(astParser,Node, Body = None):
    localContext = astParser.Context
    astParser.push_scope(GNames.process)
    
    dummy_DefaultVarSig = getDefaultVarSig()
    setDefaultVarSig(varSig.variable_t)
    ret = list()
    astParser.Context = ret
    if Body is None:
        for x in Node.body:
            ret.append( astParser.Unfold_body(x))
    else:
        ret.append( astParser.Unfold_body(Body))

    astParser.Context = localContext
    setDefaultVarSig(dummy_DefaultVarSig)
         
    astParser.pop_scope()

    return v_process_Def(ret,Node.name)

class v_process_body_Def(v_ast_base):
    def __init__(self,BodyList,name,LocalVar,dec=None):
        self.BodyList=BodyList
        self.dec = dec
        self.name = name
        self.LocalVar = LocalVar

    def get_local_var(self):
        for x in self.LocalVar:
            if x._type == "undef":
                continue
            yield x

    def get_sensitivity_list(self):
        ret =[str(self.dec[0].argList[0])]
        ret += [
            hdl.get_process_sensitivity_list(x)
            for x in self.get_local_var()
        ]
        ret = join_str(ret,Delimeter=", ",IgnoreIfEmpty=True)
        return ret

    def get_combinatorial_pull(self):
        ret =[
             hdl.get_process_combinatorial_pull(x,str(self.dec[0].argList[0]))
            for x in self.get_local_var()
        ]
        ret = join_str(ret,LineBeginning="  ",LineEnding=";\n",IgnoreIfEmpty=True)
        return ret
    def get_combinatorial_push(self):
        ret =[
            hdl.get_process_combinatorial_push(x,str(self.dec[0].argList[0]))
            for x in self.get_local_var()
        ]
        ret = join_str(ret,LineBeginning="  ",LineEnding=";\n",IgnoreIfEmpty=True)
        return ret


    def get_process_header(self):
        process_header = ""
        for x in self.LocalVar:
            process_header += hdl.get_process_header(x)
        return process_header

    def get_body(self):
        body = ""
        for x in self.BodyList:
            x_str =str(x) 
            if x_str:
                x_str = x_str.replace("\n", "\n  ")
                body += x_str+";\n  "
        return body

    def get_process_decorator(self):
        process_decorator = self.dec[0].name +"(" + str(self.dec[0].argList[0])+")"
        return process_decorator

    def __str__(self):

        sensitivity_list = self.get_sensitivity_list()
        process_header = self.get_process_header()
        body = self.get_body() 
        process_decorator = self.get_process_decorator()
        combinatorial_pull = self.get_combinatorial_pull()
        combinatorial_push = self.get_combinatorial_push()

        ret = """({sensitivity_list}) is
{process_header}
begin
{combinatorial_pull}
if {process_decorator} then
{body}
end if;
{combinatorial_push}
""".format(
    sensitivity_list=sensitivity_list,
    combinatorial_pull= combinatorial_pull,
    process_decorator=process_decorator,
    process_header=process_header,
    body=body,
    combinatorial_push=combinatorial_push
)
        return ret

        



def body_unfold_porcess_body(astParser,Node):
    if astParser.get_scope_name() != GNames.process:
        return body_unfold_porcess(astParser,Node = Node ,Body = Node)
    localContext = astParser.Context
    

    dummy_DefaultVarSig = getDefaultVarSig()
    setDefaultVarSig(varSig.variable_t)
    decorator_l = astParser.Unfold_body(Node.decorator_list)

    ret = list()
    astParser.Context = ret
    for x in Node.body:
        ret.append( astParser.Unfold_body(x))

    astParser.Context = localContext
    setDefaultVarSig(dummy_DefaultVarSig)

    return v_process_body_Def(ret,Node.name,astParser.LocalVar,decorator_l)


class v_process_body_timed_Def(v_ast_base):
    def __init__(self,BodyList,name,LocalVar,dec=None):
        self.BodyList=BodyList
        self.dec = dec
        self.name = name
        self.LocalVar = LocalVar
    
    def __str__(self):
        pull =""
        for x in self.LocalVar:
            if x._type == "undef":
                continue
            pull += x.__hdl_converter__._vhdl__Pull(x)
        push =""
        for x in self.LocalVar:
            if x._type == "undef":
                continue
            push += x.__hdl_converter__._vhdl__push(x)
        
        ret =  "\n"
        
        for x in self.LocalVar:
            ret += x.__hdl_converter__.impl_symbol_instantiation(x, "variable")
        ret += "begin\n  " 
        
        ret += pull
        for x in self.BodyList:
            x_str =str(x) 
            if x_str:
                x_str = x_str.replace("\n", "\n  ")
                ret += x_str+";\n  "
        ret += push

        return ret

def body_unfold_porcess_body_timed(astParser,Node):
    
    if astParser.get_scope_name() != GNames.process:
        return body_unfold_porcess(astParser,Node = Node ,Body = Node)

    localContext = astParser.Context
    

    dummy_DefaultVarSig = getDefaultVarSig()
    setDefaultVarSig(varSig.variable_t)
    decorator_l = astParser.Unfold_body(Node.decorator_list)

    ret = list()
    astParser.Context = ret
    for x in Node.body:
        ret.append( astParser.Unfold_body(x))

    astParser.Context = localContext
    setDefaultVarSig(dummy_DefaultVarSig)

    return v_process_body_timed_Def(ret,Node.name,astParser.LocalVar,decorator_l)

class porcess_combinational(v_ast_base):
    def __init__(self, Name, BodyList):
        self.Name =Name
        self.Body = BodyList

    def __str__(self):
        ret = "  -- begin " + self.Name +"\n"
        
        for x in self.Body:
            ret += "  " + str(x) + ";\n"
        ret += "  -- end " + self.Name 
        return ret

def body_unfold_porcess_body_combinational(astParser,Node):
    
    localContext = astParser.Context
    astParser.push_scope(GNames.process)

    dummy_DefaultVarSig = getDefaultVarSig()
    setDefaultVarSig(varSig.signal_t)
    #decorator_l = astParser.Unfold_body(Node.decorator_list)

    ret = list()
    astParser.Context = ret
    for x in Node.body:
        ret.append( astParser.Unfold_body(x))

    astParser.Context = localContext
    setDefaultVarSig(dummy_DefaultVarSig)
    
    astParser.pop_scope()

    return porcess_combinational(Node.name, ret)

class architecure_body(v_ast_base):
    def __init__(self, Name, BodyList):
        self.Name =Name
        self.Body = BodyList

    def __str__(self):
        ret = "  -- begin " + self.Name +"\n"
        
        for x in self.Body:
            v = str(x)
            if v.strip():
                ret += "  " + v + ";\n"
        ret += "  -- end " + self.Name +"\n"
        return ret

def body_unfold_architecture_body(astParser,Node):
    
    localContext = astParser.Context
    astParser.push_scope("architecture")

    dummy_DefaultVarSig = getDefaultVarSig()
    setDefaultVarSig(varSig.signal_t)
    #decorator_l = astParser.Unfold_body(Node.decorator_list)

    ret = list()
    astParser.Context = ret
    for x in Node.body:
        if type(x).__name__ == "FunctionDef":
            ret.append( astParser.Unfold_body(x))
        elif type(x).__name__ == "Assign":
            ret.append( astParser.Unfold_body(x))

    astParser.Context = localContext
    setDefaultVarSig(dummy_DefaultVarSig)
    
    astParser.pop_scope()

    return architecure_body(Node.name, ret)

class v_funDef(v_ast_base):
    def __init__(self,BodyList,dec=None):
        self.BodyList=BodyList
        self.dec = dec

    def __str__(self):
        ret = "" 
        for x in self.BodyList:
            if x is None:
                continue 
            x_str =str(x) 
            if x_str:
                x_str = x_str.replace("\n", "\n  ")
                ret += x_str+";\n  "

        return ret

    def get_type(self):
        for x in self.BodyList:
            if type(x).__name__ == "v_return":
                return x.get_type()
    



def body_unfold_functionDef(astParser,Node):
    astParser.FuncArgs.append(
        {
            "name":Node.name,
            "symbol": Node.name,
            "ScopeType": ""
        }
    )
    if isDecoratorName(Node.decorator_list, "process" ):
        return body_unfold_porcess(astParser,Node)
    if  isDecoratorName(Node.decorator_list, "rising_edge" ):
        return body_unfold_porcess_body(astParser,Node)

    if  isDecoratorName(Node.decorator_list, "timed" ):
        return body_unfold_porcess_body_timed(astParser,Node)

    if isDecoratorName(Node.decorator_list, "combinational" ): 
        return body_unfold_porcess_body_combinational(astParser,Node)

    if isDecoratorName(Node.decorator_list, "architecture" ):
        return body_unfold_architecture_body(astParser,Node)


    
    if isDecoratorName(Node.decorator_list, "hdl_export" ):
        decorator_l = []
    else:
        decorator_l = astParser.Unfold_body(Node.decorator_list)
    
    localContext = astParser.Context

    ret = list()
    astParser.Context = ret
    for x in Node.body:
        ret.append( astParser.Unfold_body(x))
        

    astParser.Context = localContext
    return v_funDef(ret,decorator_l)



class v_return (v_ast_base):
    def __init__(self,Value):
        self.value = Value

    def __str__(self):
        if self.value is None:
            return "return"
        return "return "  + str(self.value) 
    
    def get_type(self):
        if self.value is None:
            return "None"
        ty = get_symbol(self.value)
        if ty is not None and type(ty).__name__ != "str" and ty.primitive_type != "base":
            return ty.primitive_type

        ty = get_type(self.value)
        return ty

def body_unfold_return(astParser,Node):
    if Node.value is None: #procedure 
        return v_return(None)
    return v_return(astParser.Unfold_body(Node.value) )

class v_compare(v_ast_base):
    def __init__(self,lhs,ops,rhs,astParser):
        self.lhs = lhs
        self.rhs = rhs
        self.ops = ops
        self.astParser =astParser

    def __str__(self):
        if issubclass(type(self.lhs),argg_hdl_base):
            return self.lhs.__hdl_converter__.impl_compare(self.lhs, self.ops, self.rhs, self.astParser)
        
        return  str(self.lhs)  + " = " +   str(self.rhs) 

    def get_type(self):
        return "boolean"

    def _to_hdl___bool__(self,astParser):
        if type(self.rhs).__name__ == "v_name":
            rhs = astParser.get_variable(self.rhs.Value,None)
        else:
            rhs = self.rhs

        if type(self.lhs).__name__ == "v_name":
            obj = astParser.get_variable(self.lhs.Value,None)
            return obj.__hdl_converter__.impl_compare(obj, rhs)

        if self.lhs._issubclass_("v_class"):
            return self.lhs.__hdl_converter__.impl_compare(
                    self.lhs,
                    self.ops, 
                    self.rhs,
                    astParser
                )
        
        if issubclass(type(self.lhs),v_symbol):
            return self.lhs.__hdl_converter__.impl_compare(
                    self.lhs, 
                    self.ops ,
                    self.rhs,
                    astParser
                )

        if issubclass(type(self.lhs),v_enum):
            return self.lhs.__hdl_converter__.impl_compare(
                    self.lhs, 
                    self.ops ,
                    self.rhs,
                    astParser
                )
        
        raise Exception("unknown type",type(self.lhs).__name__ )

def body_unfold_Compare(astParser,Node):
    if len (Node.ops)>1:
        raise Exception("unexpected number of operators")
    return v_compare( 
            astParser.Unfold_body(Node.left),
            type(Node.ops[0]).__name__,  
            astParser.Unfold_body(Node.comparators[0]),
            astParser
        )

class v_Attribute(v_ast_base):
    def __init__(self,Attribute,Obj):
        self.obj = Obj 
        self.att = getattr(self.obj["symbol"],Attribute)
        self.att.set_vhdl_name(self.obj["symbol"].__hdl_name__+"."+Attribute)
        self.Attribute = Attribute

    def __str__(self):
        return str(self.obj) +"." + str(self.Attribute)

def body_unfold_Attribute(astParser,Node):
    val = astParser.Unfold_body(Node.value)
    
    if type(val).__name__ == "str":

        obj=astParser.getInstantByName(val)
    else:
        obj = val 
    if issubclass(type(obj),v_enum):
        return v_enum(getattr(obj._type,Node.attr))
    att = getattr(obj,Node.attr)
    
    if type(type(att)).__name__ == "EnumMeta": 
        return v_enum(att)
    
    parend = astParser.get_parant(obj)
    set_v_classType(obj, parend)
    n = hdl.impl_get_attribute(obj,Node.attr, parend)
    if type(att).__name__ == "str":
        att = to_v_object(att)
        
    att.set_vhdl_name(n,True)
    att._add_used()
    
    astParser.add_child(obj, att)
    


#    att._Inout =  obj._Inout
    astParser.FuncArgs.append({
                    "name":att.__hdl_name__,
                    "symbol": att,
                    "ScopeType": obj._Inout

        })
    return att
    
class v_Num(v_ast_base):
    def __init__(self,Value):
        self.value = Value

    def __str__(self):
        return str(self.value)

    def get_type(self):
        return "integer"

    def impl_get_value(self,ReturnToObj=None,astParser=None):
        if ReturnToObj._type =="std_logic":
            return  "'" + str(self.value)+ "'"
        if  "std_logic_vector" in ReturnToObj._type:
            if str(self) == '0':
                return " (others => '0')"
            
            return  """std_logic_vector(to_unsigned({src}, {dest}'length))""".format(
                    dest=str(ReturnToObj),
                    src = str(self.value)
            )

        if ReturnToObj._type =="integer":
            return  str(self.value)
            
        if str(self) == '0':
            ret = v_copy(ReturnToObj)
            ret.__hdl_name__ = ReturnToObj._type + "_null"
            return ret

        return "convert2"+ ReturnToObj.get_type().replace(" ","") + "(" + str(self) +")"
        
def body_unfold_Num(astParser,Node):
    return v_Num(Node.n)

class v_Str(v_ast_base):
    def __init__(self,Value):
        self.value = Value

    def __str__(self):
        return str(self.value)

    def get_type(self):
        return "str"

def body_unfold_str(astParser,Node):
    return v_Str(Node.s)

class v_variable_cration(v_ast_base):
    def __init__(self,rhs,lhs):
        self.rhs = rhs
        self.lhs = lhs



    def __str__(self):
        #return str(self.lhs.__hdl_name__) +" := "+ str(self.lhs.get_value()) 
        self.lhs.__hdl_name__ = self.rhs
        return self.lhs.__hdl_converter__.get_architecture_body(self.lhs)



    def get_type(self):
        return None

def  body_unfold_assign(astParser,Node):
    if len(Node.targets)>1:
        raise Exception(Node_line_col_2_str(astParser, Node)+"Multible Targets are not supported")


    for x in astParser.Archetecture_vars:
        if x["name"] == Node.targets[0].id:
            x["symbol"].set_vhdl_name(Node.targets[0].id,True)
            return v_noop()
    for x in astParser.LocalVar:
        if Node.targets[0].id in x.__hdl_name__:
            raise Exception(Node_line_col_2_str(astParser, Node)+" Target already exist. Use << operate to assigne new value to existing object.")

    for x in astParser.FuncArgs:
        if Node.targets[0].id == x["name"]:
            raise Exception(Node_line_col_2_str(astParser, Node)+" Target already exist. Use << operate to assigne new value to existing object.")
            


    if type(Node.targets[0]).__name__ != "Name":
        raise Exception(Node_line_col_2_str(astParser, Node)+" unknown type")
    if not astParser.get_scope_name():
        raise Exception(Node_line_col_2_str(astParser, Node)+" Symbol is not defined. use end_architecture() function at the end of the archetecture ")
    lhs = v_name (Node.targets[0].id)
    rhs =  astParser.Unfold_body(Node.value)
    rhs =  to_v_object(rhs)
    rhs.set_vhdl_name(lhs.Value, True)
    astParser.LocalVar.append(rhs)
    ret = v_variable_cration( lhs,  rhs)
    return ret


class v_name(v_ast_base):
    def __init__(self,Value):
        self.Value = Value

        

    def __str__(self):
        return str(self.Value)


    



def  body_unfold_Name(astParser,Node):
    ret = astParser.getInstantByName(Node.id)
    return ret

def handle_print(astParser,args,keywords=None):
    return v_noop()

class handle_v_switch_cl(v_ast_base):
    def __init__(self,Default, cases):
        self.Default = Default
        self.cases = cases
        self.ReturnToObj = None

    def _vhdl__setReturnType(self,ReturnToObj=None,astParser=None):
        self.ReturnToObj = ReturnToObj
        for x in self.cases:
            x._vhdl__setReturnType(ReturnToObj, astParser)



    def __str__(self):
        ret = "\n    " 
        for x in self.cases:
            x = x.impl_get_value(self.ReturnToObj)
            ret += str(x)
        default = self.Default.__hdl_converter__.impl_get_value(self.Default, self.ReturnToObj)
        
        ret += str(default) 
        return ret

def handle_v_switch(astParser,args,keywords=None):
    body = list()
    for x in args[1].elts:
        body.append(astParser.Unfold_body(x))

    return handle_v_switch_cl(astParser.Unfold_body(args[0]),body)


class handle_v_case_cl(v_ast_base):
    def __init__(self, value,pred):
        self.value = value
        self.pred = pred 

    def __str__(self):
        
        ret = str(self.value) + " when " + str(self.pred) + " else\n    "
        return ret

def handle_v_case(astParser,args,keywords=None):
    test =v_type_to_bool(astParser,astParser.Unfold_body(args[0]))
    return handle_v_case_cl(astParser.Unfold_body(args[1]), test)

class v_call(v_ast_base):
    def __init__(self,memFunc, symbol, vhdl):
        self.memFunc = memFunc    
        self.symbol  =  symbol
        
        self.__hdl_name__ =vhdl
        
        self._type = symbol._type if hasattr(symbol, "_type") else None

    def __str__(self):
            return str(self.__hdl_name__) 
        
    def get_type(self):
        return self.symbol._type

    def get_symbol(self):
        return self.symbol

def body_unfold_call_local_func(astParser,Node):

    FuncName = Node.func.id
    args = list()
    for x in Node.args:
        args.append(astParser.Unfold_body(x))

    kwargs = {}
    for x in Node.keywords:
        kwargs[x.arg] = astParser.Unfold_body(x.value) 
    
    r = astParser.local_function[Node.func.id](*args,**kwargs)
    
    f = astParser.local_function[Node.func.id]
    if hasattr(f,"description") and f.description is None: 
        f.description = v_free_function_template(f.funcrec,FuncName)
        gHDL_objectList.append(f.description)
        
        vhdl = hdl._vhdl__call_member_func(f.description, FuncName, args,astParser)

    if hasattr(f,"description") and f.description is not None: 
       
        vhdl = hdl._vhdl__call_member_func(f.description, FuncName, args,astParser)
    else:
        start = ""
        vhdl = str(Node.func.id) +"(" 
        for x in args:
            vhdl+= start + str(x)
            start  =', '
        
        vhdl += ")"

    if vhdl is None:
        astParser.Missing_template=True
        vhdl = "$$missing Template$$"

    
    ret = v_call(str(Node.func.id),r, vhdl)
    return ret


def body_unfold_call(astParser,Node):
    if hasattr(Node.func, 'id'):
        if Node.func.id in astParser._unfold_symbol_fun_arg:
            return astParser._unfold_symbol_fun_arg[Node.func.id](astParser, Node.args,Node.keywords)
        if Node.func.id in astParser.local_function:
            return body_unfold_call_local_func( astParser ,Node)
        
        raise Exception("unknown function")

    if hasattr(Node.func, 'value'):
        obj = astParser.Unfold_body(Node.func.value)
        #obj = astParser.getInstantByName(Node.func.value.id)
        memFunc = Node.func.attr
        f = getattr(obj,memFunc)

        args = list()
        for x in Node.args:
            args.append(astParser.Unfold_body(x))
        
        gf_type = isFunction()
        set_isFunction(True)
        if len(args) == 0:
            r = f()  # find out how to forward args 
        elif len(Node.args) == 1:
            r = f(args[0])  # find out how to forward args
        elif len(Node.args) == 2:
            r = f(args[0],args[1])  # find out how to forward args
        set_isFunction(gf_type)

        r = v_copy(to_v_object(r))
        vhdl = obj.__hdl_converter__._vhdl__call_member_func(obj, memFunc,[obj]+ args,astParser)
        r.set_vhdl_name(vhdl)
        ret = v_call(memFunc,r, vhdl)
        return ret

    if hasattr(Node.func, 'func'):
        return body_unfold_call(astParser,Node.func)


    raise Exception("Unknown call type")





def body_expr(astParser,Node):
    return    astParser.Unfold_body(Node.value)


class v_re_assigne_rhsift(v_ast_base):
    def __init__(self,lhs, rhs,context=None, astParser=None):
        self.lhs = lhs
        self.rhs = rhs
        self.context =context
        self.astParser = astParser
        

 

    def __str__(self):
        if issubclass(type(self.lhs),argg_hdl_base):
            return self.lhs.__hdl_converter__.impl_reasign_rshift_(self.lhs, self.rhs, astParser=self.astParser, context_str=self.context )

        return str(self.lhs) + " := " +  str(self.rhs) 

def body_RShift(astParser,Node):
    rhs =  astParser.Unfold_body(Node.right)
    lhs =  astParser.Unfold_body(Node.left)
    if issubclass( type(lhs),argg_hdl_base) and issubclass( type(rhs),argg_hdl_base):
        rhs.__Driver__ = astParser.ContextName[-1]
         
        return v_re_assigne_rhsift(lhs, rhs,context=astParser.ContextName[-1],astParser=astParser)

    err_msg = argg_hdl_error(
        astParser.sourceFileName,
        Node.lineno, 
        Node.col_offset,
        type(lhs).__name__, 
        "right shift is only supported for argg_hdl objects"
    )
    raise Exception(err_msg,lhs)


class v_re_assigne(v_ast_base):
    def __init__(self,lhs, rhs,context=None, astParser=None):
        self.lhs = lhs
        self.rhs = rhs
        self.context =context
        self.astParser = astParser
        

 

    def __str__(self):
        if issubclass(type(self.lhs),argg_hdl_base):
            return self.lhs.__hdl_converter__.impl_reasign(self.lhs, self.rhs, astParser=self.astParser, context_str=self.context )

        return str(self.lhs) + " := " +  str(self.rhs) 

def body_LShift(astParser,Node):
    rhs =  astParser.Unfold_body(Node.right)
    lhs =  astParser.Unfold_body(Node.left)
    
    if issubclass( type(lhs),argg_hdl_base):
        lhs = lhs.__hdl_converter__.impl_reasign_type(lhs)
        if issubclass( type(rhs),argg_hdl_base):
            rhs = rhs.__hdl_converter__.impl_get_value(rhs, lhs,astParser)
        else:
            rhs = rhs.impl_get_value(lhs,astParser)


        if astParser.ContextName[-1] == 'process':
            lhs.__Driver__ = 'process'
        elif astParser.ContextName[-1] == 'function':
            lhs.__Driver__ = 'function'
        else:
            lhs << rhs
        
        return v_re_assigne(lhs, rhs,context=astParser.ContextName[-1],astParser=astParser)
           

    var = astParser.get_variable(lhs.Value, Node)
    #print(str(lhs) + " << " + str(rhs))     
    return v_re_assigne(var, rhs,context=astParser.ContextName[-1],astParser=astParser)

def hasNumericalValue(symb):
    if type(symb).__name__ == "int":
        return True
    if type(symb).__name__ == "v_Num":
        return True

    return False
class v_add(v_ast_base):
    def __init__(self,lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs
        self._type = lhs._type
        self.Value = str(self.lhs) + " + " +  str(self.rhs) 
        

    def get_value(self):
        return value(self.lhs) + value(self.rhs)

    def get_type(self):
        return self._type

    def __str__(self):
        if issubclass(type(self.lhs),argg_hdl_base):
            return self.lhs.__hdl_converter__.impl_add(self.lhs, self.rhs)

        return str(self.lhs) + " + " +  str(self.rhs) 

    def get_symbol(self):
        return self.lhs

def body_add(astParser,Node):
    rhs =  astParser.Unfold_body(Node.right)
    lhs =  astParser.Unfold_body(Node.left)
    if issubclass( type(lhs),argg_hdl_base):
        return v_add(lhs, rhs)

    if hasNumericalValue(lhs) and hasNumericalValue(rhs):
        return v_Num(value(lhs) + value(rhs))
        
    #var = astParser.get_variable(lhs.Value, Node)

    return v_add(lhs, rhs)

class v_sub(v_ast_base):
    def __init__(self,lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs
        self._type = lhs._type
        

        

    def __str__(self):
        if issubclass(type(self.lhs),argg_hdl_base):
            return self.lhs.__hdl_converter__._vhdl__Sub(self.lhs, self.rhs)

        return str(self.lhs) + " - " +  str(self.rhs) 

def body_sub(astParser,Node):
    rhs =  astParser.Unfold_body(Node.right)
    lhs =  astParser.Unfold_body(Node.left)
    if issubclass( type(lhs),argg_hdl_base):
        return v_sub(lhs, rhs)

    var = astParser.get_variable(lhs.Value, Node)

    return v_sub(var, rhs)



class v_multi(v_ast_base):
    def __init__(self,lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs
        self._type = lhs._type
        

        

    def __str__(self):
        if issubclass(type(self.lhs),argg_hdl_base):
            return self.lhs.__hdl_converter__._vhdl__multi(self.lhs, self.rhs)

        return str(self.lhs) + " * " +  str(self.rhs) 

def body_multi(astParser,Node):
    rhs =  astParser.Unfold_body(Node.right)
    lhs =  astParser.Unfold_body(Node.left)
    
    

    return v_multi(lhs, rhs)

class v_stream_assigne(v_ast_base):
    def __init__(self,lhs, rhs,StreamOut,lhsEntity,context=None):
        self.lhsEntity = lhsEntity
        self.lhs = lhs
        self.rhs = rhs
        self.context =context
        self._StreamOut =None
        if StreamOut is not None:
            self._StreamOut = StreamOut

        

 

    def __str__(self):
        ret = ""
        if issubclass(type(self.lhsEntity), v_ast_base):
            ret+= str(self.lhsEntity) +";\n  "
            
        if issubclass(type(self.lhs),argg_hdl_base):
            ret += self.lhs.__hdl_converter__.impl_reasign(self.lhs, self.rhs)

        else:
            ret += str(self.lhs) + " := " +  str(self.rhs) 

        return ret


def body_bitOr(astParser,Node):
    rhs =  astParser.Unfold_body(Node.right)
    lhs =  astParser.Unfold_body(Node.left)
    ret = lhs | rhs
    
    ret.astParser = astParser
            
    return ret


def body_BinOP(astParser,Node):
    optype = type(Node.op).__name__
        
    return astParser._Unfold_body[optype](astParser,Node)


class v_named_C(v_ast_base):
    def __init__(self,Value):
        self.Value = Value
        self.__hdl_name__ =str(Value)
        
        

        
    def get_symbol(self):
        ret = v_int(self.Value)
        ret.set_vhdl_name(str(self.Value), True)
        return ret

    def __str__(self):
        return str(self.Value)



def body_Named_constant(astParser,Node):
    return v_named_C(Node.value)


def v_type_to_bool(astParser,obj):


    if type(obj).__name__ == "v_name":
        obj = astParser.get_variable(obj.Value,None)

    if type(obj).__name__ == "v_compare":
        return obj._to_hdl___bool__( astParser)

    if issubclass(type(obj),argg_hdl_base):
        return obj.__hdl_converter__._to_hdl___bool__(obj, astParser)

    if type(obj).__name__ == "v_call":
        return  obj.symbol.__hdl_converter__._to_hdl___bool__(obj.symbol,astParser)




    if obj.get_type() == 'boolean':
        return obj
class v_if(v_ast_base):
    def __init__(self,ifEsleIfElse, test, body,oreEsle):
        self.ifEsleIfElse = ifEsleIfElse    
        self.test=test
        self.body = body
        self.oreEsle  = oreEsle
        self.isElse = False


    def __str__(self):
        
        if self.isElse:
            gIndent.deinc()
            ret ="\n" +str(gIndent) +  "elsif ("
            gIndent.inc()
        else:
            ret ="\n" +str(gIndent) +  "if ("
        
            gIndent.inc()
        
        ret += str(self.test) +") then \n"+str(gIndent)
        for x in self.body:
            x_str =str(x)
            if x_str:
               # x_str.replace("\n","\n  ")
                ret += x_str +";\n"+str(gIndent)

        
        oreelse =""
        if len(self.oreEsle) > 0 and type(self.oreEsle[0]).__name__ != "v_if":
            gIndent.deinc()
            oreelse+="\n"+ str(gIndent) + "else"
            gIndent.inc()
            oreelse += "\n"+str(gIndent) 
            for x in self.oreEsle:
                oreelse += str(x)+";\n"+str(gIndent) 
        
        else:
            for x in self.oreEsle:
                x.isElse = True
                oreelse += str(x)
            

        ret += oreelse
        gIndent.deinc()
        if self.isElse:
            ret +=""
        else:
            ret +="\n" +str(gIndent) +  "end if" 
        

        return ret


def body_if(astParser,Node):
    
    ifEsleIfElse = "if"
    test =v_type_to_bool(astParser, astParser.Unfold_body(Node.test))
    body = astParser.Unfold_body(Node.body)
    localContext = astParser.Context
    oreEsle = list ()
    astParser.Context  = oreEsle
    for x in Node.orelse:
        oreEsle.append(astParser.Unfold_body(x))
    astParser.Context =localContext 
    return v_if(ifEsleIfElse, test, body,oreEsle)


def body_list(astParser,Node):
    localContext = astParser.Context
    ret = list()
    astParser.Context  = ret
    for x in Node:
        l = astParser.Unfold_body(x)
        ret.append(l)
    astParser.Context =localContext 
    return ret




class v_boolOp(v_ast_base):
    def __init__(self,elements,op):
        self.elements = elements
 
        self.op = op

    def __str__(self):
        op = type(self.op).__name__
        if op == "And":
            op = " and "
        elif op == "Or":
            op = " or "
        ret = "( "
        start = ""
        for x in self.elements:
            ret += start + str(x) 
            start = op
        ret += ") "
        return ret

    def get_type(self):
        return "boolean"




def body_BoolOp(astParser, Node):
    elements = list()
    for x in Node.values:
        e = astParser.Unfold_body(x)
        e = v_type_to_bool(astParser,e)
        elements.append(e)


    op = Node.op
    return v_boolOp(elements,op)

class v_UnaryOP(v_ast_base):
    def __init__(self,obj,op):
        self.obj = obj
        self.op = op
        self._type = "boolean"

    def __str__(self):
        op = type(self.op).__name__
        if op == "Not":
            op = " not "

        return   op +  " ( " + str(self.obj) +" ) " 

    def get_symbol(self):
        return self.obj
    def get_type(self):
        return "boolean"

def body_unfol_Not(astParser,Node):
    arg = astParser.Unfold_body(Node.operand)
    arg = v_type_to_bool(astParser,arg)
    #print_cnvt(arg)

    return v_UnaryOP(arg, Node.op)

class v_USubOP(v_ast_base):
    def __init__(self,obj):
        self.obj = obj
        self._type = obj._type
    
    def __str__(self):

        return  " -(" + str(self.obj) +")"

def body_unfol_USub(astParser,Node):
    arg = astParser.Unfold_body(Node.operand)
    if issubclass(type(arg),argg_hdl_base) and arg._varSigConst==varSig.unnamed_const:
        arg.nextValue = -arg.nextValue
        arg.set_vhdl_name(str(arg.nextValue) , True)
        return arg

    return v_USubOP(arg)

def body_UnaryOP(astParser,Node):
    ftype = type(Node.op).__name__
    return astParser._Unfold_body[ftype](astParser,Node)
    arg = astParser.Unfold_body(Node.operand)
    arg = v_type_to_bool(astParser,arg)
    #print_cnvt(arg)

    return v_UnaryOP(arg, Node.op)



def body_subscript(astParser,Node):
    value = astParser.Unfold_body(Node.value)
    sl  = astParser.Unfold_body(Node.slice)
    return value.__hdl_converter__.impl_slice(value, sl,astParser)

def body_index(astParser,Node):
    sl  = astParser.Unfold_body(Node.value)
    return sl 

class v_decorator:
    def __init__(self,name,argList):
        self.name=name
        self.argList=argList

    def get_sensitivity_list(self):
        return str(self.argList[0])

    def get_prefix(self):
        return self.name + "(" + str(self.argList[0]) +")"

def handle_rising_edge(astParser, symb,keyword=None):
    l = list()
    for x in symb:
        s = astParser.Unfold_body(x)
        l.append(s)

    return v_decorator("rising_edge", l )


def handle_v_create(astParser, symb):
    raise Exception("function not implemented")


class v_yield(v_ast_base):
    def __init__(self,Arg):
        self.arg = Arg

    def __str__(self):


        return   "wait for " + str(self.arg.symbol) 
        
def body_unfold_yield(astParser,Node):
    
    arg = astParser.Unfold_body(Node.value)
    return v_yield(arg)



class v_for(v_ast_base):
    range_counter = 0
    def __init__(self,arg,body):
        self.arg = arg
        self.body = body

    def __str__(self):
        start = "for " + str(self.arg) +" loop \n"
        ind = str(gIndent)
        gIndent.inc()
        ret = join_str( self.body , start=start,end=ind+"end loop",LineEnding=";\n", LineBeginning=str(gIndent),IgnoreIfEmpty=True, RemoveEmptyElements = True)
        gIndent.deinc()
        return ret

def v_for_reset():
    v_for.range_counter = 0

g_add_global_reset_function(v_for_reset)


def body_unfold_for(astParser,Node):
    if hasattr(Node.iter,"id"):
        return for_loop_ranged_based(astParser,Node)

    if type(Node.iter).__name__ == "Call" and Node.iter.func.id == "range":
        return for_loop_indexed_based(astParser,Node)
    
    return for_loop_ranged_based2(astParser,Node)

def for_body(astParser,Node):
    localContext = astParser.Context
    ret = list()
    astParser.Context  = ret
    for x in Node:
        l = astParser.Unfold_body(x)
        ret.append(l)
    astParser.Context =localContext 
    return ret

def for_loop_ranged_based2(astParser,Node):
        
    obj=astParser.Unfold_body(Node.iter)

    itt = "i"+str(v_for.range_counter)
    v_for.range_counter += 1
    arg = itt + " in 0 to " + str(obj.__hdl_converter__.length(obj)) +" -1"


    vhdl_name = str(Node.target.id)
    buff =  astParser.try_get_variable(vhdl_name)

    if buff is None:
        buff = v_copy(obj.Internal_Type)
        buff.__hdl_name__ = str(obj) + "("+itt+")"
        buff._varSigConst = varSig.reference_t
        astParser.FuncArgs.append({'ScopeType':"", 'name' : vhdl_name,'symbol': buff})
    else:
        raise Exception("name already used")


    body = for_body(astParser,Node.body)
    astParser.FuncArgs =  [ x for x in astParser.FuncArgs if x['name'] != vhdl_name ]

    return v_for(arg,body)


def for_loop_ranged_based(astParser,Node):
    itt = Node.iter.id
    obj=astParser.getInstantByName(Node.iter.id)

    itt = "i"+str(v_for.range_counter)
    v_for.range_counter += 1
    arg = itt + " in 0 to " + obj.__hdl_converter__.length(obj) +" -1"


    vhdl_name = str(Node.target.id)
    buff =  astParser.try_get_variable(vhdl_name)

    if buff is None:
        buff = v_copy(obj.Internal_Type)
        buff.__hdl_name__ = str(obj) + "("+itt+")"
        buff._varSigConst = varSig.reference_t
        astParser.FuncArgs.append({'ScopeType':"", 'name' : vhdl_name,'symbol': buff})
    else:
        raise Exception("name already used")


    body = for_body(astParser,Node.body)
    astParser.FuncArgs =  [ x for x in astParser.FuncArgs if x['name'] != vhdl_name ]

    return v_for(arg,body)

def for_loop_indexed_based(astParser,Node):
    args = list()
    for x in Node.iter.args:
        l = astParser.Unfold_body(x)
        args.append(l)
    
    #obj=astParser.getInstantByName(Node.iter.id)

    itt = "i"+str(v_for.range_counter)
    v_for.range_counter += 1
    arg = itt + " in 0 to " + str(args[0]) +" -1"


    vhdl_name = str(Node.target.id)
    buff =  astParser.try_get_variable(vhdl_name)

    if buff is None:
        buff = v_int()
        buff.__hdl_name__ = itt
        buff._varSigConst = varSig.reference_t
        astParser.FuncArgs.append({'ScopeType':"", 'name' : vhdl_name,'symbol': buff})
    else:
        raise Exception("name already used")


    body = for_body(astParser,Node.body)
    astParser.FuncArgs =  [ x for x in astParser.FuncArgs if x['name'] != vhdl_name ]

    return v_for(arg,body)

def body_handle_len(astParser,args,keywords=None):
    l = astParser.Unfold_body(args[0])
    return l.__hdl_converter__.length(l)

def  body_end_architecture(astParser,args,keywords=None):
    return v_noop()


def body_unfold_Break(astParser,args,keywords=None):
    return "exit"

def body_unfold_Continue(astParser,args,keywords=None):
    return "next"

def body_Constant(astParser,Node,keywords=None):
    if type(Node.value).__name__== 'bool':
        ret = v_bool(Default=Node.value)
        ret.set_vhdl_name(str(Node.value), True)
        ret._varSigConst = varSig.unnamed_const
        return ret
        
    ret = v_int(Node.value)
    ret.set_vhdl_name(str(Node.value), True)
    ret._varSigConst = varSig.unnamed_const
    return ret


class v_slice(v_ast_base):
    def __init__(self,lower,upper,step):
        super().__init__()
        self.lower = lower
        self.upper = upper
        self.step  = step
        self.reversed  =  False
        self.sourceOBJ  =  None

    def set_source(self,sourceOBJ):
        self.sourceOBJ = sourceOBJ

    def __str__(self):

        if self.upper is None:
            upper = str(self.sourceOBJ.__hdl_converter__.length(self.sourceOBJ)) + " -1 " 
        else:
            upper = str(self.upper) 
            if upper.lstrip('-').isnumeric():
                upper = int(upper)
                if upper < 0 :
                    upper = str(self.sourceOBJ.__hdl_converter__.length(self.sourceOBJ)) + " - " + str( abs(upper - 1))
                else:
                    upper = str(int(upper) - 1 )
            else:
                upper += " - 1 "
        
        if self.reversed:
            return str(self.lower) + " to "  + upper

        return  upper  + "  downto  " + str(self.lower) 

def body_unfold_slice(astParser,Node,keywords=None):
    lower = astParser.Unfold_body( Node.lower) if Node.lower else None
    upper = astParser.Unfold_body( Node.upper) if Node.upper else None
    step = astParser.Unfold_body( Node.step) if Node.step else None
    ret = v_slice(lower, upper, step)
    return ret

def body_unfold_BitAnd(astParser,Node,keywords=None):
    rhs =  astParser.Unfold_body(Node.right)
    lhs =  astParser.Unfold_body(Node.left)
    ret = lhs.__hdl_converter__.impl_bit_and(lhs, rhs,  astParser)
    return ret
