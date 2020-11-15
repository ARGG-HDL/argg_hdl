from argg_hdl.ast.ast_classes.ast_base import v_ast_base, add_class
import  argg_hdl.argg_hdl_hdl_converter as  hdl
from argg_hdl.argg_hdl_v_symbol import v_int
from argg_hdl.argg_hdl_base import argg_hdl_base0

class index_handler(v_ast_base):
    def __init__(self, index) -> None:
        self.index = index
        self.Source = None


    def set_source(self,source):
        self.Source = source

    def __str__(self):
        sl = self.index
        if issubclass(type(sl),argg_hdl_base0):
            sl = hdl.impl_get_value(sl,ReturnToObj=v_int(),astParser=None)
        return str(sl)


def body_subscript(astParser,Node):
    value = astParser.Unfold_body(Node.value)
    sl  = astParser.Unfold_body(Node.slice)
    sl.set_source(value)
    return hdl.impl_slice(value, sl,astParser)

def body_index(astParser,Node):
    sl  = astParser.Unfold_body(Node.value)
    return index_handler(sl)

add_class("Subscript", body_subscript)
add_class("Index", body_index)