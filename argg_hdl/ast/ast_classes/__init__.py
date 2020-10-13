import argg_hdl.ast.ast_classes.ast_base as ast_base
import argg_hdl.ast.ast_classes.ast_slice as slice
import argg_hdl.ast.ast_classes.ast_for as v_for
import argg_hdl.ast.ast_classes.ast_yield as ast_yiel
import argg_hdl.ast.ast_classes.ast_return as ast_return
import argg_hdl.ast.ast_classes.ast_if as ast_if
import argg_hdl.ast.ast_classes.ast_compare as ast_compare
import argg_hdl.ast.ast_classes.ast_Attribute as ast_Attribute
import argg_hdl.ast.ast_classes.ast_op_bool as ast_op_bool
import argg_hdl.ast.ast_classes.ast_op_bit_or as ast_op_bit_or
import argg_hdl.ast.ast_classes.ast_op_multi as ast_op_multi
import argg_hdl.ast.ast_classes.ast_op_bit_and as ast_op_bit_and
import argg_hdl.ast.ast_classes.ast_op_add as ast_op_add
import argg_hdl.ast.ast_classes.ast_op_not as ast_op_not
import argg_hdl.ast.ast_classes.ast_op_unitarty_sub as ast_op_unitarty_sub
import argg_hdl.ast.ast_classes.ast_function_architeture
import argg_hdl.ast.ast_classes.ast_function_porcess_combinational
import argg_hdl.ast.ast_classes.ast_function_porcess_timed
import argg_hdl.ast.ast_classes.ast_function_process
import argg_hdl.ast.ast_classes.ast_function_process_body
import argg_hdl.ast.ast_classes.ast_FunctionDef
import argg_hdl.ast.ast_classes.ast_switch
import argg_hdl.ast.ast_classes.ast_continue
import argg_hdl.ast.ast_classes.ast_op_sub
import argg_hdl.ast.ast_classes.ast_Num
import argg_hdl.ast.ast_classes.ast_op
import argg_hdl.ast.ast_classes.ast_assignment



g_ast_class_register  = ast_base.g_ast_class_register
g_ast_function_call  = ast_base.g_ast_function_call
