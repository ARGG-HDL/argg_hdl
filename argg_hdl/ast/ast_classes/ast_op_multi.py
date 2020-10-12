from argg_hdl.ast.ast_classes.ast_base import v_ast_base, add_class
import  argg_hdl.argg_hdl_hdl_converter as  hdl
from argg_hdl.argg_hdl_base import argg_hdl_base


class v_multi(v_ast_base):
    def __init__(self,lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs
        self._type = lhs._type
        

        

    def __str__(self):
        if issubclass(type(self.lhs),argg_hdl_base):
            return hdl.impl_multi(self.lhs, self.rhs)

        return str(self.lhs) + " * " +  str(self.rhs) 

def body_multi(astParser,Node):
    rhs =  astParser.Unfold_body(Node.right)
    lhs =  astParser.Unfold_body(Node.left)
    
    

    return v_multi(lhs, rhs)


add_class("Mult", body_multi)
