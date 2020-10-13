from argg_hdl.ast.ast_classes.ast_base import v_ast_base, add_class
from argg_hdl.argg_hdl_lib_enums import getDefaultVarSig, setDefaultVarSig,varSig


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
    astParser.push_scope("process")
    
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


add_class("process", body_unfold_porcess)

