
gprim_hdl_converter = {

}


def get_primitive_hdl_converter(typeName):
    return gprim_hdl_converter[typeName]


def add_primitive_hdl_converter(typeName, hdl_converter):
    gprim_hdl_converter[typeName] = hdl_converter