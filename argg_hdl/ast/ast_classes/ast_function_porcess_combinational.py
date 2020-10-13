from argg_hdl.ast.ast_classes.ast_base import v_ast_base, add_class
from argg_hdl.argg_hdl_lib_enums import getDefaultVarSig, setDefaultVarSig,varSig



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
    astParser.push_scope("process")

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

add_class("combinational", body_unfold_porcess_body_combinational)

