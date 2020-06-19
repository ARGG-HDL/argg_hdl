


def get_dependency_objects(obj, dep_list):
    return obj.__hdl_converter__.get_dependency_objects(obj, dep_list)

def ops2str(obj, ops):
    return obj.__hdl_converter__.ops2str(ops)


def FlagFor_TemplateMissing(obj):
    obj.__hdl_converter__.FlagFor_TemplateMissing(obj)

def reset_TemplateMissing(obj):
    obj.__hdl_converter__.reset_TemplateMissing(obj)

def isTemplateMissing(obj):
    return obj.__hdl_converter__.isTemplateMissing(obj)

def IsSucessfullConverted(obj):
    return obj.__hdl_converter__.IsSucessfullConverted(obj)


def convert_all_packages(obj, ouputFolder,x,FilesDone):
    return obj.__hdl_converter__.convert_all_packages(obj, ouputFolder,x,FilesDone)

def convert_all_entities(obj, ouputFolder,x,FilesDone):
    return obj.__hdl_converter__.convert_all_entities(obj, ouputFolder,x,FilesDone)

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

def parse_file(obj):
    return obj.__hdl_converter__.parse_file(obj)

def includes(obj, name,parent):
    return obj.__hdl_converter__.includes(obj, name,parent)

def recordMember(obj, name,parent,Inout=None):
    return obj.__hdl_converter__.recordMember(obj, name,parent,Inout)


def recordMemberDefault(obj,name,parent,Inout=None):
    return obj.__hdl_converter__.recordMemberDefault(obj,name,parent,Inout)

def getHeader(obj, name,parent):
    return obj.__hdl_converter__.getHeader(obj,name,parent)

def getFuncArg(obj,name,parent):
    return obj.__hdl_converter__.getFuncArg(obj,name,parent)

def getBody(obj, name,parent):
    return obj.__hdl_converter__.getBody(obj,name,parent)

def _vhdl_make_port(obj, name):
    return obj.__hdl_converter__._vhdl_make_port(obj,name)

def _vhdl_get_attribute(obj, attName):
    return obj.__hdl_converter__._vhdl_get_attribute(obj, attName)

def _vhdl_slice(obj, sl,astParser=None):
    return obj.__hdl_converter__._vhdl_slice(obj, sl,astParser)

def _vhdl__compare(obj, ops, rhs, astParser =None):
    return obj.__hdl_converter__._vhdl__compare(obj, ops, rhs, astParser )

def _vhdl__add(obj,args):
    return obj.__hdl_converter__._vhdl__add(obj,args)

def _vhdl__Sub(obj,args):
    return obj.__hdl_converter__._vhdl__Sub(obj,args)

def _to_hdl___bool__(obj, astParser):
    return obj.__hdl_converter__._to_hdl___bool__(obj, astParser)

def _vhdl__BitAnd(obj,rhs,astParser):
    return obj.__hdl_converter__._vhdl__BitAnd(obj,rhs,astParser)

def function_name_modifier(obj,name, varSigSuffix):
    return obj.__hdl_converter__.function_name_modifier(obj,name, varSigSuffix)

def _vhdl__getValue(obj, ReturnToObj=None,astParser=None):
    return obj.__hdl_converter__._vhdl__getValue(obj, ReturnToObj,astParser)

def _vhdl__reasign_type(obj ):
    return obj.__hdl_converter__._vhdl__reasign_type(obj)

def _vhdl__reasign(obj, rhs, astParser=None,context_str=None):
    return obj.__hdl_converter__._vhdl__reasign(obj, rhs, astParser,context_str)

def _vhdl__reasign_rshift_(obj, rhs, astParser=None,context_str=None):
    return obj.__hdl_converter__._vhdl__reasign_rshift_(obj, rhs, astParser,context_str)

def get_get_call_member_function(obj, name, args):
    return obj.__hdl_converter__.get_get_call_member_function(obj, name, args)

def _vhdl__call_member_func(obj, name, args, astParser=None):
    return obj.__hdl_converter__._vhdl__call_member_func(obj, name, args, astParser)

def _vhdl__DefineSymbol(obj, VarSymb="variable"):
    return obj.__hdl_converter__._vhdl__DefineSymbol(obj, VarSymb)

def get_architecture_header(obj):
    return obj.__hdl_converter__.get_architecture_header(obj)

def get_architecture_body(obj):
    return obj.__hdl_converter__.get_architecture_body(obj)

def get_packet_definition(obj):
    return obj.__hdl_converter__.get_packet_definition(obj)

def get_entity_definition(obj):
    return obj.__hdl_converter__.get_entity_definition(obj)

def get_port_list(obj):
    return obj.__hdl_converter__.get_port_list(obj)

def get_process_header(obj):
    return obj.__hdl_converter__.get_process_header(obj)

def _vhdl__Pull(obj):
    return obj.__hdl_converter__._vhdl__Pull(obj)

def _vhdl__push(obj):
    return obj.__hdl_converter__._vhdl__push(obj)


def get_assiment_op(obj):
    return obj.__hdl_converter__.get_assiment_op(obj)


def InOut_t2str2(obj, inOut):
    return obj.__hdl_converter__.InOut_t2str2(inOut)

def InOut_t2str(obj):
    return obj.__hdl_converter__.InOut_t2str(obj)

def get_default_value(obj):
    return obj.__hdl_converter__.get_default_value(obj)

def extract_conversion_types(obj, exclude_class_type=None,filter_inout=None):
    return obj.__hdl_converter__.extract_conversion_types(obj, exclude_class_type, filter_inout)

def get_Name_array(obj):
    return obj.__hdl_converter__.get_Name_array(obj)

def length(obj):
    return obj.__hdl_converter__.length(obj)

def to_arglist(obj, name,parent,withDefault = False,astParser=None):
    return obj.__hdl_converter__.to_arglist(obj, name,parent, withDefault, astParser)

def get_inout_type_recursive(obj):
    return obj.__hdl_converter__.get_inout_type_recursive(obj)

def Has_pushpull_function(obj, pushpull):
    return obj.__hdl_converter__.Has_pushpull_function(obj, pushpull)

    

