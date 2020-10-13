from argg_hdl.ast.ast_classes.ast_base import v_ast_base, add_class
import  argg_hdl.argg_hdl_hdl_converter as  hdl
from argg_hdl.argg_hdl_base import argg_hdl_base





class v_re_assigne(v_ast_base):
    def __init__(self,lhs, rhs,context=None, astParser=None):
        self.lhs = lhs
        self.rhs = rhs
        self.context =context
        self.astParser = astParser
        

 

    def __str__(self):
        if issubclass(type(self.lhs),argg_hdl_base):
            return hdl.impl_reasign(self.lhs, self.rhs, astParser=self.astParser, context_str=self.context )

        return str(self.lhs) + " := " +  str(self.rhs) 

def body_LShift(astParser,Node):
    rhs =  astParser.Unfold_body(Node.right)
    lhs =  astParser.Unfold_body(Node.left)
    
    if issubclass( type(lhs),argg_hdl_base):
        lhs = hdl.impl_reasign_type(lhs)
        if issubclass( type(rhs),argg_hdl_base):
            rhs =hdl.impl_get_value(rhs, lhs,astParser)
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


add_class("LShift",body_LShift)