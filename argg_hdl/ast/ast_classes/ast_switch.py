
from argg_hdl.ast.ast_classes.ast_base import add_ast_function_call, v_ast_base, add_class
import  argg_hdl.argg_hdl_hdl_converter as  hdl
from argg_hdl.ast.ast_classes.ast_type_to_bool import v_type_to_bool


class handle_v_switch_cl(v_ast_base):
    def __init__(self,Default, cases):
        self.Default = Default
        self.cases = cases
        self.ReturnToObj = None

    def _vhdl__setReturnType(self,ReturnToObj=None,astParser=None):
        self.ReturnToObj = ReturnToObj
        for x in self.cases:
            x._vhdl__setReturnType(ReturnToObj, astParser)



    def __str__(self):
        ret = "\n    " 
        for x in self.cases:
            x = x.impl_get_value(self.ReturnToObj)
            ret += str(x)
        default = hdl.impl_get_value(self.Default, self.ReturnToObj)
        
        ret += str(default) 
        return ret

def handle_v_switch(astParser,args,keywords=None):
    body = list()
    for x in args[1].elts:
        body.append(astParser.Unfold_body(x))

    return handle_v_switch_cl(astParser.Unfold_body(args[0]),body)


class handle_v_case_cl(v_ast_base):
    def __init__(self, value,pred):
        self.value = value
        self.pred = pred 

    def __str__(self):
        
        ret = str(self.value) + " when " + str(self.pred) + " else\n    "
        return ret

def handle_v_case(astParser,args,keywords=None):
    test =v_type_to_bool(astParser,astParser.Unfold_body(args[0]))
    return handle_v_case_cl(astParser.Unfold_body(args[1]), test)

add_ast_function_call("v_switch", handle_v_switch)
add_ast_function_call("v_case"  , handle_v_case)