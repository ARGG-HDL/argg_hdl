

from argg_hdl.argg_hdl_base import *
from argg_hdl.argg_hdl_v_enum import * 
from argg_hdl.argg_hdl_to_v_object import *
from argg_hdl.argg_hdl_v_symbol  import *

import  argg_hdl.argg_hdl_hdl_converter as  hdl
from argg_hdl.ast.argg_hdl_ast_hdl_error import argg_hdl_error

from argg_hdl.ast.ast_classes.ast_base import v_ast_base ,gIndent
from argg_hdl.ast.ast_classes.ast_type_to_bool import v_type_to_bool
from argg_hdl.ast.ast_classes.ast_noop import v_noop





def unfold_Str(astParser, strNode):
    return strNode.s
def unfold_num(astParser, NumNode):
    return NumNode.n


def Unfold_call(astParser, callNode):
        
    return astParser._unfold_symbol_fun_arg[callNode.func.id](astParser, callNode.args)



    








def port_in_to_vhdl(astParser,Node,Keywords=None):
    return port_in(astParser.unfold_argList(Node[0]) )

def port_out_to_vhdl(astParser,Node,Keywords=None):
    return port_out(astParser.unfold_argList(Node[0]) )

def variable_port_in_to_vhdl(astParser,Node,Keywords=None):
    return variable_port_in(astParser.unfold_argList(Node[0]) )

def variable_port_out_to_vhdl(astParser,Node,Keywords=None):
    return  variable_port_out(astParser.unfold_argList(Node[0]) )

def v_symbol_to_vhdl(astParser,Node,Keywords=None):
    args = list()
    for x in Node:
        x_obj = astParser.Unfold_body(x)
        if type(x_obj).__name__ == "v_Num":
            args.append(x_obj.value )
        else:
            args.append(x_obj)

    kwargs = {}
    if Keywords:
        for x in Keywords:
            if x.arg =='varSigConst':
                temp = astParser.Unfold_body(x.value).Value 
                temp._add_input()
                kwargs[x.arg] = temp
            else:
                temp = astParser.Unfold_body(x.value) 
                temp._add_input()
                kwargs[x.arg] = temp

    return v_symbol(*args,**kwargs)  


def v_slv_to_vhdl(astParser,Node,Keywords=None):
    args = list()
    for x in Node:
        x_obj = astParser.Unfold_body(x)
        if type(x_obj).__name__ == "v_Num":
            args.append(x_obj.value )
        else:
            args.append(x_obj)

    kwargs = {}
    if Keywords:
        for x in Keywords:
            if x.arg =='varSigConst':
                kwargs[x.arg] = astParser.Unfold_body(x.value).Value 
            else:
                kwargs[x.arg] = astParser.Unfold_body(x.value) 

    return v_slv(*args,**kwargs)


def v_sl_to_vhdl(astParser,Node,Keywords=None):
    if len(Node) == 1:
        return v_sl(InOut_t.input_t, astParser.unfold_argList(Node[0]) )
    
    return v_sl(InOut_t.input_t )
        
        
def v_int_to_vhdl(astParser,Node,Keywords=None):
    return v_int()


def v_bool_to_vhdl(astParser,Node,Keywords=None):
    return v_bool()












def handle_print(astParser,args,keywords=None):
    return v_noop()









class v_stream_assigne(v_ast_base):
    def __init__(self,lhs, rhs,StreamOut,lhsEntity,context=None):
        self.lhsEntity = lhsEntity
        self.lhs = lhs
        self.rhs = rhs
        self.context =context
        self._StreamOut =None
        if StreamOut is not None:
            self._StreamOut = StreamOut

        

 

    def __str__(self):
        ret = ""
        if issubclass(type(self.lhsEntity), v_ast_base):
            ret+= str(self.lhsEntity) +";\n  "
            
        if issubclass(type(self.lhs),argg_hdl_base):
            ret += hdl.impl_reasign(self.lhs, self.rhs)

        else:
            ret += str(self.lhs) + " := " +  str(self.rhs) 

        return ret



















class v_decorator:
    def __init__(self,name,argList):
        self.name=name
        self.argList=argList

    def get_sensitivity_list(self):
        return str(self.argList[0])

    def get_prefix(self):
        return self.name + "(" + str(self.argList[0]) +")"

def handle_rising_edge(astParser, symb,keyword=None):
    l = list()
    for x in symb:
        s = astParser.Unfold_body(x)
        l.append(s)

    return v_decorator("rising_edge", l )


def handle_v_create(astParser, symb):
    raise Exception("function not implemented")





def body_handle_len(astParser,args,keywords=None):
    l = astParser.Unfold_body(args[0])
    return hdl.length(l)

def  body_end_architecture(astParser,args,keywords=None):
    return v_noop()







