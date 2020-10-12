from argg_hdl.converter.argg_hdl__primitive_type_converter_base import *


class v_uinteger_converter(v_symbol_converter):
    primitive_type = "uinteger"

    def __init__(self, inc_str):
        super().__init__(inc_str)



    def impl_reasign(self, obj: "v_symbol", rhs, astParser=None, context_str=None):
        if astParser:
            astParser.add_write(obj)
        obj._add_output()
        target = str(obj)


        if issubclass(type(rhs), argg_hdl_base0) and str(obj.__Driver__) != 'process':
            obj.__Driver__ = rhs

        if isProcess():
            obj.__Driver__ = 'process'

        asOp = obj.__hdl_converter__.get_assiment_op(obj)

        if issubclass(type(rhs), argg_hdl_base) and "std_logic_vector" in rhs._type:
            return target + asOp + " to_integer(unsigned(" + str(rhs) + "))"

        return target + asOp + str(rhs)


add_primitive_hdl_converter(v_uinteger_converter.primitive_type, v_uinteger_converter)
