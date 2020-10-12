from argg_hdl.ast.ast_classes.ast_base import v_ast_base, add_class
import  argg_hdl.argg_hdl_hdl_converter as  hdl

class v_yield(v_ast_base):
    def __init__(self,Arg):
        self.arg = Arg

    def __str__(self):


        return   "wait for " + str(self.arg.symbol) 
        
def body_unfold_yield(astParser,Node):
    
    arg = astParser.Unfold_body(Node.value)
    return v_yield(arg)

add_class( "Yield",body_unfold_yield)