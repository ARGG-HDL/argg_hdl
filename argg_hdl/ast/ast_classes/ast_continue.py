from argg_hdl.ast.ast_classes.ast_base import add_class

def body_unfold_Continue(astParser,args,keywords=None):
    return "next"

add_class('Continue' , body_unfold_Continue)