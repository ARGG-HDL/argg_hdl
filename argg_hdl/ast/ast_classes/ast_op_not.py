from argg_hdl.ast.ast_classes.ast_base import v_ast_base, add_class
from argg_hdl.ast.ast_classes.ast_type_to_bool import v_type_to_bool

class v_UnaryOP(v_ast_base):
    def __init__(self,obj,op):
        self.obj = obj
        self.op = op
        self._type = "boolean"

    def __str__(self):
        op = type(self.op).__name__
        if op == "Not":
            op = " not "

        return   op +  " ( " + str(self.obj) +" ) " 

    def get_symbol(self):
        return self.obj
    def get_type(self):
        return "boolean"

def body_unfol_Not(astParser,Node):
    arg = astParser.Unfold_body(Node.operand)
    arg = v_type_to_bool(astParser,arg)
    #print_cnvt(arg)

    return v_UnaryOP(arg, Node.op)


add_class('Not', body_unfol_Not)