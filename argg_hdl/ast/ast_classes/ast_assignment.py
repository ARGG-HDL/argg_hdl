from argg_hdl.ast.ast_classes.ast_base import v_ast_base, add_class,gIndent,Node_line_col_2_str 
import  argg_hdl.argg_hdl_hdl_converter as  hdl
from argg_hdl.argg_hdl_to_v_object import to_v_object
from argg_hdl.ast.ast_classes.ast_noop import v_noop

class v_name(v_ast_base):
    def __init__(self,Value):
        self.Value = Value
    def __str__(self):
        return str(self.Value)



class v_variable_cration(v_ast_base):
    def __init__(self,rhs,lhs):
        self.rhs = rhs
        self.lhs = lhs



    def __str__(self):
        #return str(self.lhs.__hdl_name__) +" := "+ str(self.lhs.get_value()) 
        self.lhs.__hdl_name__ = self.rhs
        return hdl.impl_architecture_body(self.lhs)



    def get_type(self):
        return None

def  body_unfold_assign(astParser,Node):
    if len(Node.targets)>1:
        raise Exception(Node_line_col_2_str(astParser, Node)+"Multible Targets are not supported")


    for x in astParser.Archetecture_vars:
        if x["name"] == Node.targets[0].id:
            x["symbol"].set_vhdl_name(Node.targets[0].id,True)
            return v_noop()
    for x in astParser.LocalVar:
        if Node.targets[0].id in x.__hdl_name__:
            raise Exception(Node_line_col_2_str(astParser, Node)+" Target already exist. Use << operate to assigne new value to existing object.")

    for x in astParser.FuncArgs:
        if Node.targets[0].id == x["name"]:
            raise Exception(Node_line_col_2_str(astParser, Node)+" Target already exist. Use << operate to assigne new value to existing object.")
            


    if type(Node.targets[0]).__name__ != "Name":
        raise Exception(Node_line_col_2_str(astParser, Node)+" unknown type")
    if not astParser.get_scope_name():
        raise Exception(Node_line_col_2_str(astParser, Node)+" Symbol is not defined. use end_architecture() function at the end of the archetecture ")
    lhs = v_name (Node.targets[0].id)
    rhs =  astParser.Unfold_body(Node.value)
    rhs =  to_v_object(rhs)
    rhs.set_vhdl_name(lhs.Value, True)
    astParser.LocalVar.append(rhs)
    ret = v_variable_cration( lhs,  rhs)
    return ret


add_class("Assign" ,body_unfold_assign)