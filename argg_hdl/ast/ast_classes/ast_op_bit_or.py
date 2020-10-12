from argg_hdl.ast.ast_classes.ast_base import v_ast_base, add_class

def body_bitOr(astParser,Node):
    rhs =  astParser.Unfold_body(Node.right)
    lhs =  astParser.Unfold_body(Node.left)
    ret = lhs | rhs
    
    ret.astParser = astParser
            
    return ret

add_class("BitOr", body_bitOr)
