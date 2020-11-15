from argg_hdl.argg_hdl_object_factory import impl_constructor




def is_argg_hdl_obj(obj):
    return impl_constructor("is_argg_hdl_obj")(obj)

def is_variable(obj):
    return impl_constructor("is_variable")(obj)

def is_signal(obj):
    return impl_constructor("is_signal")(obj)

def is_handle_class(obj):
    return impl_constructor("is_handle_class")(obj)


def is_trans_class(obj):
    return impl_constructor("is_trans_class")(obj)

def set_v_classType(obj,parant_obj):
    return impl_constructor("set_v_classType")(obj,parant_obj)

def is_symbol(obj):
    return impl_constructor("is_symbol")(obj)