from argg_hdl.ast.ast_classes.ast_base import add_class

def body_expr(astParser,Node):
    return    astParser.Unfold_body(Node.value)


add_class("Expr", body_expr)