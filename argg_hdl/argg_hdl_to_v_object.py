
import os,sys,inspect

import argg_hdl as ah




def to_v_object(ObjIn):
    if issubclass(type(ObjIn),ah.argg_hdl_base):
        return ObjIn
    if issubclass(type(ObjIn),ah.argg_hdl_base0):
        return ObjIn
    elif type(ObjIn).__name__ == "v_stream_assigne":
        return ObjIn
    elif type(ObjIn).__name__ == "EnumMeta":
        return ah.v_enum(ObjIn)
    elif type(ObjIn).__name__ == 'bool':
        return ah.v_symbol("boolean", str(ObjIn))
    elif type(ObjIn).__name__ == 'v_Num':
        return ah.v_symbol("integer", str(ObjIn))
    elif type(ObjIn).__name__ == 'str':
        return ah.v_symbol("undef", str(ObjIn))
    
    elif type(ObjIn).__name__ == 'v_call':
        return ObjIn.symbol

    elif type(ObjIn).__name__ == "v_named_C":
        return to_v_object(ObjIn.Value)

    elif type(ObjIn).__name__ == "int":
        return ah.v_symbol("integer", str(ObjIn))

    elif ObjIn == None:
        return ah.v_symbol("None", str(ObjIn))

        
    raise Exception("unknown type")