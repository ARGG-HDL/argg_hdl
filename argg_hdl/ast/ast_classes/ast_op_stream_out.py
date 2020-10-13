from argg_hdl.ast.ast_classes.ast_base import v_ast_base, add_class
import  argg_hdl.argg_hdl_hdl_converter as  hdl
from argg_hdl.ast.argg_hdl_ast_hdl_error import argg_hdl_error
from argg_hdl.argg_hdl_base import argg_hdl_base

class v_re_assigne_rhsift(v_ast_base):
    def __init__(self,lhs, rhs,context=None, astParser=None):
        self.lhs = lhs
        self.rhs = rhs
        self.context =context
        self.astParser = astParser
        

 

    def __str__(self):
        if issubclass(type(self.lhs),argg_hdl_base):
            return hdl.impl_reasign_rshift_(self.lhs, self.rhs, astParser=self.astParser, context_str=self.context )

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

add_class("RShift",body_RShift)