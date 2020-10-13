from argg_hdl.ast.ast_classes.ast_base import add_class
from argg_hdl.argg_hdl_v_symbol  import v_bool, v_int
from argg_hdl.argg_hdl_lib_enums  import varSig


def body_Constant(astParser,Node,keywords=None):
    if type(Node.value).__name__== 'bool':
        ret = v_bool(Default=Node.value)
        ret.set_vhdl_name(str(Node.value), True)
        ret._varSigConst = varSig.unnamed_const
        return ret
        
    ret = v_int(Node.value)
    ret.set_vhdl_name(str(Node.value), True)
    ret._varSigConst = varSig.unnamed_const
    return ret

add_class("Constant", body_Constant)
