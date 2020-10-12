from argg_hdl.converter.argg_hdl__primitive_type_converter_base import *


class v_sl_converter(v_symbol_converter):
    primitive_type = "std_logic"
    
    def __init__(self,inc_str):
        super().__init__(inc_str)



    def impl_compare(self,obj:"v_symbol", ops, rhs, astParser):
        astParser.add_read(obj)
        obj._add_input()
        if issubclass(type(rhs),argg_hdl_base):
            astParser.add_read(rhs)
            rhs._add_input()

        
        value = str(rhs).lower()
        if value == "true":
            rhs = "1"
        elif value == "false":
            rhs = "0"            
        return str(obj) + " "+ hdl.ops2str(obj, ops) +" '" +  str(rhs) +"'"





    def impl_reasign(self, obj:"v_symbol", rhs, astParser=None,context_str=None):
        if astParser:
            astParser.add_write(obj)
        obj._add_output()
        target = str(obj)


        if issubclass(type(rhs),argg_hdl_base0)  and str( obj.__Driver__) != 'process':
            obj.__Driver__ = rhs
        
        if isProcess():
            obj.__Driver__ = 'process'
        
        asOp = hdl.get_assiment_op(obj)
        if issubclass(type(rhs),argg_hdl_base0):
            return target + asOp + str(hdl.impl_get_value(rhs, obj)) 
        return target + asOp+  str(rhs) 


add_primitive_hdl_converter(v_sl_converter.primitive_type , v_sl_converter )
