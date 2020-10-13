from argg_hdl.ast.ast_classes.ast_base import v_ast_base, add_class
from argg_hdl.argg_hdl_base import v_copy


  
class v_Num(v_ast_base):
    def __init__(self,Value):
        self.value = Value

    def __str__(self):
        return str(self.value)

    def get_type(self):
        return "integer"

    def impl_get_value(self,ReturnToObj=None,astParser=None):
        if ReturnToObj._type =="std_logic":
            return  "'" + str(self.value)+ "'"
        if  "std_logic_vector" in ReturnToObj._type:
            if str(self) == '0':
                return " (others => '0')"
            
            return  """std_logic_vector(to_unsigned({src}, {dest}'length))""".format(
                    dest=str(ReturnToObj),
                    src = str(self.value)
            )

        if ReturnToObj._type =="integer":
            return  str(self.value)
            
        if str(self) == '0':
            ret = v_copy(ReturnToObj)
            ret.__hdl_name__ = ReturnToObj._type + "_null"
            return ret

        return "convert2"+ ReturnToObj.get_type().replace(" ","") + "(" + str(self) +")"
        
def body_unfold_Num(astParser,Node):
    return v_Num(Node.n)


add_class("Num", body_unfold_Num)