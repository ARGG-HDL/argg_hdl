from argg_hdl.ast.ast_classes.ast_base import v_ast_base, add_class
import  argg_hdl.argg_hdl_hdl_converter as  hdl
from argg_hdl.argg_hdl_base_helpers import get_symbol, get_type

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


add_class( "Return",body_unfold_return)