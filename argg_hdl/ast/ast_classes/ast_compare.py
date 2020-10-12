from argg_hdl.ast.ast_classes.ast_base import v_ast_base, add_class,gIndent
import  argg_hdl.argg_hdl_hdl_converter as  hdl
from argg_hdl.argg_hdl_base import argg_hdl_base
from argg_hdl.argg_hdl_v_enum import v_enum 
from argg_hdl.argg_hdl_v_symbol  import v_symbol

class v_compare(v_ast_base):
    def __init__(self,lhs,ops,rhs,astParser):
        self.lhs = lhs
        self.rhs = rhs
        self.ops = ops
        self.astParser =astParser

    def __str__(self):
        if issubclass(type(self.lhs),argg_hdl_base):
            return hdl.impl_compare(self.lhs, self.ops, self.rhs, self.astParser)
        
        return  str(self.lhs)  + " = " +   str(self.rhs) 

    def get_type(self):
        return "boolean"

    def impl_to_bool(self,astParser):
        if type(self.rhs).__name__ == "v_name":
            rhs = astParser.get_variable(self.rhs.Value,None)
        else:
            rhs = self.rhs

        if type(self.lhs).__name__ == "v_name":
            obj = astParser.get_variable(self.lhs.Value,None)
            return hdl.impl_compare(obj, rhs)

        if self.lhs._issubclass_("v_class"):
            return hdl.impl_compare(
                    self.lhs,
                    self.ops, 
                    self.rhs,
                    astParser
                )
        
        if issubclass(type(self.lhs),v_symbol):
            return hdl.impl_compare(
                    self.lhs, 
                    self.ops ,
                    self.rhs,
                    astParser
                )

        if issubclass(type(self.lhs),v_enum):
            return hdl.impl_compare(
                    self.lhs, 
                    self.ops ,
                    self.rhs,
                    astParser
                )
        
        raise Exception("unknown type",type(self.lhs).__name__ )

def body_unfold_Compare(astParser,Node):
    if len (Node.ops)>1:
        raise Exception("unexpected number of operators")
    return v_compare( 
            astParser.Unfold_body(Node.left),
            type(Node.ops[0]).__name__,  
            astParser.Unfold_body(Node.comparators[0]),
            astParser
        )


add_class("Compare", body_unfold_Compare)