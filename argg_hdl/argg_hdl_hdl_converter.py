def get_dependency_objects(obj, dep_list):
    return obj.__hdl_converter__.get_dependency_objects(obj, dep_list)


def ops2str(obj, ops):
    return obj.__hdl_converter__.ops2str(ops)


def get_MemfunctionCalls(obj):
    return obj.__hdl_converter__.get_MemfunctionCalls(obj)


def FlagFor_TemplateMissing(obj):
    obj.__hdl_converter__.FlagFor_TemplateMissing(obj)


def reset_TemplateMissing(obj):
    obj.__hdl_converter__.reset_TemplateMissing(obj)


def isTemplateMissing(obj):
    return obj.__hdl_converter__.isTemplateMissing(obj)


def IsSucessfullConverted(obj):
    return obj.__hdl_converter__.IsSucessfullConverted(obj)


def convert_all_packages(obj, ouputFolder, x, FilesDone):
    return obj.__hdl_converter__.convert_all_packages(obj, ouputFolder, x, FilesDone)


def convert_all_entities(obj, ouputFolder, x, FilesDone):
    return obj.__hdl_converter__.convert_all_entities(obj, ouputFolder, x, FilesDone)


def convert_all_impl(obj, ouputFolder, FilesDone):
    return obj.__hdl_converter__.convert_all_impl(obj, ouputFolder, FilesDone)


def convert_all(obj, ouputFolder):
    return obj.__hdl_converter__.convert_all(obj, ouputFolder)


def get_primary_object(obj):
    return obj.__hdl_converter__.get_primary_object(obj)


def get_packet_file_name(obj):
    return obj.__hdl_converter__.get_packet_file_name(obj)


def get_packet_file_content(obj):
    return obj.__hdl_converter__.get_packet_file_content(obj)


def get_enity_file_content(obj):
    return obj.__hdl_converter__.get_enity_file_content(obj)


def get_entity_file_name(obj):
    return obj.__hdl_converter__.get_entity_file_name(obj)


def get_type_simple(obj):
    return obj.__hdl_converter__.get_type_simple(obj)

def get_type_simple_template(obj):
    return obj.__hdl_converter__.get_type_simple_template(obj)
    
def impl_constructor(obj):
    return obj.__hdl_converter__.impl_constructor(obj)

def parse_file(obj):
    return obj.__hdl_converter__.parse_file(obj)


def impl_includes(obj, name, parent):
    return obj.__hdl_converter__.impl_includes(obj, name, parent)

def def_includes(obj, name, parent):
    return obj.__hdl_converter__.def_includes(obj, name, parent)


def def_record_Member(obj, name, parent, Inout=None):
    return obj.__hdl_converter__.def_record_Member(obj, name, parent, Inout)


def def_record_Member_Default(obj, name, parent, Inout=None):
    return obj.__hdl_converter__.def_record_Member_Default(obj, name, parent, Inout)


def def_packet_header(obj, name, parent):
    return obj.__hdl_converter__.def_packet_header(obj, name, parent)




def def_packet_body(obj, name, parent):
    return obj.__hdl_converter__.def_packet_body(obj, name, parent)


def impl_entity_port(obj, name):
    return obj.__hdl_converter__.impl_entity_port(obj, name)

def impl_function_argument(obj, func_arg, arg):
    return obj.__hdl_converter__.impl_function_argument(obj, func_arg, arg)

def impl_get_attribute(obj, attName,parent = None):
    return obj.__hdl_converter__.impl_get_attribute(obj, attName, parent)


def impl_slice(obj, sl, astParser=None):
    return obj.__hdl_converter__.impl_slice(obj, sl, astParser)


def impl_compare(obj, ops, rhs, astParser=None):
    return obj.__hdl_converter__.impl_compare(obj, ops, rhs, astParser)


def impl_add(obj, args):
    return obj.__hdl_converter__.impl_add(obj, args)


def impl_sub(obj, args):
    return obj.__hdl_converter__.impl_sub(obj, args)


def impl_to_bool(obj, astParser):
    return obj.__hdl_converter__.impl_to_bool(obj, astParser)


def impl_bit_and(obj, rhs, astParser):
    return obj.__hdl_converter__.impl_bit_and(obj, rhs, astParser)


def function_name_modifier(obj, name, varSigSuffix):
    return obj.__hdl_converter__.function_name_modifier(obj, name, varSigSuffix)


def impl_get_value(obj, ReturnToObj=None, astParser=None):
    return obj.__hdl_converter__.impl_get_value(obj, ReturnToObj, astParser)


def impl_reasign_type(obj):
    return obj.__hdl_converter__.impl_reasign_type(obj)


def impl_reasign(obj, rhs, astParser=None, context_str=None):
    return obj.__hdl_converter__.impl_reasign(obj, rhs, astParser, context_str)


def impl_reasign_rshift_(obj, rhs, astParser=None, context_str=None):
    return obj.__hdl_converter__.impl_reasign_rshift_(obj, rhs, astParser, context_str)


def get_call_member_function(obj, name, args):
    return obj.__hdl_converter__.get_call_member_function(obj, name, args)


def impl_function_call(obj, name, args, astParser=None):
    return obj.__hdl_converter__.impl_function_call(obj=obj, name=name, args=args, astParser=astParser)


def impl_symbol_instantiation(obj, VarSymb="variable"):
    return obj.__hdl_converter__.impl_symbol_instantiation(obj, VarSymb)


def impl_architecture_header(obj):
    prepare_for_conversion(obj)
    return obj.__hdl_converter__.impl_architecture_header(obj)


def impl_architecture_body(obj):
    return obj.__hdl_converter__.impl_architecture_body(obj)


def impl_add(obj,args):
    return obj.__hdl_converter__.impl_add(obj, args)
    
    
def impl_sub(obj,args):
    return obj.__hdl_converter__.impl_sub(obj, args)
    

def impl_multi(obj,args):
    return obj.__hdl_converter__.impl_multi(obj, args)
    




def def_entity_port(obj):
    prepare_for_conversion(obj)
    return obj.__hdl_converter__.def_entity_port(obj)


def impl_process_header(obj):
    return obj.__hdl_converter__.impl_process_header(obj)

def impl_process_sensitivity_list(obj):
    return obj.__hdl_converter__.impl_process_sensitivity_list(obj)

def impl_process_pull(obj,clk):
    return obj.__hdl_converter__.impl_process_pull(obj,clk)
    
def impl_process_push(obj,clk):
    return obj.__hdl_converter__.impl_process_push(obj,clk)





def get_assiment_op(obj):
    return obj.__hdl_converter__.get_assiment_op(obj)

def get_Inout(obj,parent):
    return obj.__hdl_converter__.get_Inout(obj,parent)    

def InOut_t2str2(obj, inOut):
    return obj.__hdl_converter__.InOut_t2str2(inOut)


def InOut_t2str(obj):
    return obj.__hdl_converter__.InOut_t2str(obj)


def get_default_value(obj):
    return obj.__hdl_converter__.get_default_value(obj)


def extract_conversion_types(obj, exclude_class_type=None, filter_inout=None):
    return obj.__hdl_converter__.extract_conversion_types(obj, exclude_class_type, filter_inout)


def get_Name_array(obj):
    return obj.__hdl_converter__.get_Name_array(obj)


def length(obj):
    return obj.__hdl_converter__.length(obj)


def to_arglist(obj, name, parent, withDefault=False, astParser=None):
    return obj.__hdl_converter__.to_arglist(obj, name, parent, withDefault, astParser)


def get_inout_type_recursive(obj):
    return obj.__hdl_converter__.get_inout_type_recursive(obj)


def Has_pushpull_function(obj, pushpull):
    return obj.__hdl_converter__.Has_pushpull_function(obj, pushpull)


def get_free_symbols(obj, name, parent_list=[]):
    return obj.__hdl_converter__.get_free_symbols(obj,name, parent_list)


def get_component_suffix(obj, Inout_type, varsignal_type):
    return obj.__hdl_converter__.get_component_suffix(obj, Inout_type, varsignal_type)


def prepare_for_conversion(obj):
    return obj.__hdl_converter__.prepare_for_conversion(obj)

def get_HDL_name(obj, parent,suffix):
    return obj.__hdl_converter__.get_HDL_name(obj,parent,suffix)

def impl_get_init_values(obj,parent=None, InOut_Filter=None, VaribleSignalFilter = None,ForceExpand=False):
    return obj.__hdl_converter__.impl_get_init_values(obj, parent, InOut_Filter, VaribleSignalFilter ,ForceExpand)


def get_extractedTypes(obj):
    primary = get_primary_object(obj)
    prepare_for_conversion(primary)
    return primary.__hdl_converter__.extractedTypes
