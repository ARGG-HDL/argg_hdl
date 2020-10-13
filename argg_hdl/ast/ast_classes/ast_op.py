from argg_hdl.ast.ast_classes.ast_base import add_class

def body_BinOP(astParser,Node):
    optype = type(Node.op).__name__
        
    return astParser._Unfold_body[optype](astParser,Node)

add_class("BinOp", body_BinOP)