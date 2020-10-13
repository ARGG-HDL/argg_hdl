from argg_hdl.ast.ast_classes.ast_base import  add_class

def body_UnaryOP(astParser,Node):
    ftype = type(Node.op).__name__
    return astParser._Unfold_body[ftype](astParser,Node)


add_class("UnaryOp", body_UnaryOP)