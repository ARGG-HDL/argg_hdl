from argg_hdl.ast.ast_classes.ast_base import add_class


def body_unfold_Break(astParser,args,keywords=None):
    return "exit"

add_class('Break' , body_unfold_Break)