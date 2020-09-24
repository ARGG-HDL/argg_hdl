from argg_hdl.converter.argg_hdl__primitive_type_converter_base import *


class v_bool_converter(v_symbol_converter):
    primitive_type = "boolean"

    def __init__(self, inc_str):
        super().__init__(inc_str)


add_primitive_hdl_converter(v_bool_converter.primitive_type, v_bool_converter )