from argg_hdl.ast.ast_classes.ast_base import v_ast_base, add_class
import  argg_hdl.argg_hdl_hdl_converter as  hdl
from argg_hdl.argg_hdl_lib_enums import getDefaultVarSig, setDefaultVarSig,varSig
from argg_hdl.ast.ast_classes.ast_function_process import  body_unfold_porcess

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
            pull += hdl._vhdl__Pull(x)
        push =""
        for x in self.LocalVar:
            if x._type == "undef":
                continue
            push += hdl._vhdl__push(x)
        
        ret =  "\n"
        
        for x in self.LocalVar:
            ret += hdl.impl_symbol_instantiation(x, "variable")
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
    
    if astParser.get_scope_name() != "process":
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

add_class("timed",body_unfold_porcess_body_timed)

