from argg_hdl.argg_hdl_base import argg_hdl_base
import  argg_hdl.argg_hdl_hdl_converter as  hdl

def v_type_to_bool(astParser,obj):


    if type(obj).__name__ == "v_name":
        obj = astParser.get_variable(obj.Value,None)

    if type(obj).__name__ == "v_compare":
        return obj.impl_to_bool( astParser)

    if issubclass(type(obj),argg_hdl_base):
        return hdl.impl_to_bool(obj, astParser)

    if type(obj).__name__ == "v_call":
        return  hdl.impl_to_bool(obj.symbol,astParser)




    if obj.get_type() == 'boolean':
        return obj

