
from argg_hdl.ast.ast_classes.ast_base import add_class, v_ast_base

class v_Str(v_ast_base):
    def __init__(self,Value):
        self.value = Value

    def __str__(self):
        return str(self.value)

    def get_type(self):
        return "str"

def body_unfold_str(astParser,Node):
    return v_Str(Node.s)


add_class("Str",body_unfold_str)

