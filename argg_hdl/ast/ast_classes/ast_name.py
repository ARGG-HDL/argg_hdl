from argg_hdl.ast.ast_classes.ast_base import add_class



def  body_unfold_Name(astParser,Node):
    ret = astParser.getInstantByName(Node.id)
    return ret

add_class("Name", body_unfold_Name)