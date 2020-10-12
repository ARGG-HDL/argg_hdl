from argg_hdl.ast.ast_classes.ast_base import v_ast_base, add_class,gIndent
import  argg_hdl.argg_hdl_hdl_converter as  hdl
from argg_hdl.argg_hdl_v_enum import v_enum 
from argg_hdl.argg_hdl_to_v_object import to_v_object
from argg_hdl.argg_hdl_base import set_v_classType

class v_Attribute(v_ast_base):
    def __init__(self,Attribute,Obj):
        self.obj = Obj 
        self.att = getattr(self.obj["symbol"],Attribute)
        self.att.set_vhdl_name(self.obj["symbol"].__hdl_name__+"."+Attribute)
        self.Attribute = Attribute

    def __str__(self):
        return str(self.obj) +"." + str(self.Attribute)

def body_unfold_Attribute(astParser,Node):
    val = astParser.Unfold_body(Node.value)
    
    if type(val).__name__ == "str":

        obj=astParser.getInstantByName(val)
    else:
        obj = val 
    if issubclass(type(obj),v_enum):
        return v_enum(getattr(obj._type,Node.attr))
    att = getattr(obj,Node.attr)
    
    if type(type(att)).__name__ == "EnumMeta": 
        return v_enum(att)
    
    parend = astParser.get_parant(obj)
    set_v_classType(obj, parend)
    n = hdl.impl_get_attribute(obj,Node.attr, parend)
    if type(att).__name__ == "str":
        att = to_v_object(att)
        
    att.set_vhdl_name(n,True)
    att._add_used()
    
    astParser.add_child(obj, att)
    


#    att._Inout =  obj._Inout
    astParser.FuncArgs.append({
                    "name":att.__hdl_name__,
                    "symbol": att,
                    "ScopeType": obj._Inout

        })
    return att
  

add_class("Attribute" ,body_unfold_Attribute)