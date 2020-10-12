from argg_hdl.ast.ast_classes.ast_base import v_ast_base, add_class
from argg_hdl.ast.ast_classes.ast_type_to_bool import v_type_to_bool


class v_boolOp(v_ast_base):
    def __init__(self,elements,op):
        self.elements = elements
 
        self.op = op

    def __str__(self):
        op = type(self.op).__name__
        if op == "And":
            op = " and "
        elif op == "Or":
            op = " or "
        ret = "( "
        start = ""
        for x in self.elements:
            ret += start + str(x) 
            start = op
        ret += ") "
        return ret

    def get_type(self):
        return "boolean"




def body_BoolOp(astParser, Node):
    elements = list()
    for x in Node.values:
        e = astParser.Unfold_body(x)
        e = v_type_to_bool(astParser,e)
        elements.append(e)


    op = Node.op
    return v_boolOp(elements,op)

add_class("BoolOp"   , body_BoolOp)