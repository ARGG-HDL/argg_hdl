from argg_hdl.ast.ast_classes.ast_base import v_ast_base, add_class, add_ast_function_call
from argg_hdl.argg_hdl_lib_enums import getDefaultVarSig, setDefaultVarSig,varSig
from argg_hdl.ast.ast_classes.ast_noop import v_noop

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


add_class("architecture",body_unfold_architecture_body)

def  body_end_architecture(astParser,args,keywords=None):
    return v_noop()

add_ast_function_call("end_architecture",body_end_architecture)
