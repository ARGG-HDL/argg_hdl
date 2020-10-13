from argg_hdl.ast.ast_classes.ast_base import v_ast_base, add_class
from argg_hdl.argg_hdl_v_symbol import v_int
class v_named_C(v_ast_base):
    def __init__(self,Value):
        self.Value = Value
        self.__hdl_name__ =str(Value)
        
        

        
    def get_symbol(self):
        ret = v_int(self.Value)
        ret.set_vhdl_name(str(self.Value), True)
        return ret

    def __str__(self):
        return str(self.Value)



def body_Named_constant(astParser,Node):
    return v_named_C(Node.value)


add_class("NameConstant",body_Named_constant)