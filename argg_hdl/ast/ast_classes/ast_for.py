from argg_hdl.ast.ast_classes.ast_base import v_ast_base, add_class,gIndent
import  argg_hdl.argg_hdl_hdl_converter as  hdl
from argg_hdl.argg_hdl_base import *
from argg_hdl.argg_hdl_v_enum import * 
from argg_hdl.argg_hdl_to_v_object import *
from argg_hdl.argg_hdl_v_symbol  import *




class v_for(v_ast_base):
    range_counter = 0
    def __init__(self,arg,body):
        self.arg = arg
        self.body = body

    def __str__(self):
        start = "for " + str(self.arg) +" loop \n"
        ind = str(gIndent)
        gIndent.inc()
        ret = join_str( self.body , start=start,end=ind+"end loop",LineEnding=";\n", LineBeginning=str(gIndent),IgnoreIfEmpty=True, RemoveEmptyElements = True)
        gIndent.deinc()
        return ret

def v_for_reset():
    v_for.range_counter = 0

g_add_global_reset_function(v_for_reset)


def body_unfold_for(astParser,Node):
    if hasattr(Node.iter,"id"):
        return for_loop_ranged_based(astParser,Node)

    if type(Node.iter).__name__ == "Call" and Node.iter.func.id == "range":
        return for_loop_indexed_based(astParser,Node)
    
    return for_loop_ranged_based2(astParser,Node)

def for_body(astParser,Node):
    localContext = astParser.Context
    ret = list()
    astParser.Context  = ret
    for x in Node:
        l = astParser.Unfold_body(x)
        ret.append(l)
    astParser.Context =localContext 
    return ret

def for_loop_ranged_based2(astParser,Node):
        
    obj=astParser.Unfold_body(Node.iter)

    itt = "i"+str(v_for.range_counter)
    v_for.range_counter += 1
    arg = itt + " in 0 to " + str(hdl.length(obj)) +" -1"


    vhdl_name = str(Node.target.id)
    buff =  astParser.try_get_variable(vhdl_name)

    if buff is None:
        buff = v_copy(obj.Internal_Type)
        buff.__hdl_name__ = str(obj) + "("+itt+")"
        buff._varSigConst = varSig.reference_t
        astParser.FuncArgs.append({'ScopeType':"", 'name' : vhdl_name,'symbol': buff})
    else:
        raise Exception("name already used")


    body = for_body(astParser,Node.body)
    astParser.FuncArgs =  [ x for x in astParser.FuncArgs if x['name'] != vhdl_name ]

    return v_for(arg,body)


def for_loop_ranged_based(astParser,Node):
    itt = Node.iter.id
    obj=astParser.getInstantByName(Node.iter.id)

    itt = "i"+str(v_for.range_counter)
    v_for.range_counter += 1
    arg = itt + " in 0 to " + hdl.length(obj) +" -1"


    vhdl_name = str(Node.target.id)
    buff =  astParser.try_get_variable(vhdl_name)

    if buff is None:
        buff = v_copy(obj.Internal_Type)
        buff.__hdl_name__ = str(obj) + "("+itt+")"
        buff._varSigConst = varSig.reference_t
        astParser.FuncArgs.append({'ScopeType':"", 'name' : vhdl_name,'symbol': buff})
    else:
        raise Exception("name already used")


    body = for_body(astParser,Node.body)
    astParser.FuncArgs =  [ x for x in astParser.FuncArgs if x['name'] != vhdl_name ]

    return v_for(arg,body)

def for_loop_indexed_based(astParser,Node):
    args = list()
    for x in Node.iter.args:
        l = astParser.Unfold_body(x)
        args.append(l)
    
    #obj=astParser.getInstantByName(Node.iter.id)

    itt = "i"+str(v_for.range_counter)
    v_for.range_counter += 1
    arg = itt + " in 0 to " + str(args[0]) +" -1"


    vhdl_name = str(Node.target.id)
    buff =  astParser.try_get_variable(vhdl_name)

    if buff is None:
        buff = v_int()
        buff.__hdl_name__ = itt
        buff._varSigConst = varSig.reference_t
        astParser.FuncArgs.append({'ScopeType':"", 'name' : vhdl_name,'symbol': buff})
    else:
        raise Exception("name already used")


    body = for_body(astParser,Node.body)
    astParser.FuncArgs =  [ x for x in astParser.FuncArgs if x['name'] != vhdl_name ]

    return v_for(arg,body)


add_class("For", body_unfold_for)