from argg_hdl.argg_hdl_base import indent
class v_ast_base:

    def __str__(self):
        return type(self).__name__

    def get_type(self):
        return ""
        
    def impl_get_value(self,ReturnToObj=None,astParser=None):
        self._vhdl__setReturnType(ReturnToObj, astParser)
        return str(self)    

    def _vhdl__setReturnType(self,ReturnToObj=None,astParser=None):
        pass

    def get_symbol(self):
        return None

        
gIndent = indent()

g_ast_class_register = {}

def add_class(Node_name,class_factory):
    g_ast_class_register[Node_name] = class_factory


g_ast_function_call = {}

def add_ast_function_call(Node_name,class_factory):
    g_ast_class_register[Node_name] = class_factory

