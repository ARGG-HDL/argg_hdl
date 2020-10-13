

from argg_hdl.argg_hdl_base import *
from argg_hdl.argg_hdl_v_enum import * 
from argg_hdl.argg_hdl_to_v_object import *
from argg_hdl.argg_hdl_v_symbol  import *
from argg_hdl.argg_hdl_v_function  import v_free_function_template
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





class v_Str(v_ast_base):
    def __init__(self,Value):
        self.value = Value

    def __str__(self):
        return str(self.value)

    def get_type(self):
        return "str"

def body_unfold_str(astParser,Node):
    return v_Str(Node.s)





    



def  body_unfold_Name(astParser,Node):
    ret = astParser.getInstantByName(Node.id)
    return ret

def handle_print(astParser,args,keywords=None):
    return v_noop()



class v_call(v_ast_base):
    def __init__(self,memFunc, symbol, vhdl):
        self.memFunc = memFunc    
        self.symbol  =  symbol
        
        self.__hdl_name__ =vhdl
        
        self._type = symbol._type if hasattr(symbol, "_type") else None

    def __str__(self):
            return str(self.__hdl_name__) 
        
    def get_type(self):
        return self.symbol._type

    def get_symbol(self):
        return self.symbol

def body_unfold_call_local_func(astParser,Node):

    FuncName = Node.func.id
    args = list()
    for x in Node.args:
        args.append(astParser.Unfold_body(x))

    kwargs = {}
    for x in Node.keywords:
        kwargs[x.arg] = astParser.Unfold_body(x.value) 
    
    r = astParser.local_function[Node.func.id](*args,**kwargs)
    
    f = astParser.local_function[Node.func.id]
    if hasattr(f,"description") and f.description is None: 
        f.description = v_free_function_template(f.funcrec,FuncName)
        gHDL_objectList.append(f.description)
        
        vhdl = hdl.impl_function_call(f.description, FuncName, args,astParser)

    if hasattr(f,"description") and f.description is not None: 
       
        vhdl = hdl.impl_function_call(f.description, FuncName, args,astParser)
    else:
        start = ""
        vhdl = str(Node.func.id) +"(" 
        for x in args:
            vhdl+= start + str(x)
            start  =', '
        
        vhdl += ")"

    if vhdl is None:
        astParser.Missing_template=True
        vhdl = "$$missing Template$$"

    
    ret = v_call(str(Node.func.id),r, vhdl)
    return ret


def body_unfold_call(astParser,Node):
    if hasattr(Node.func, 'id'):
        if Node.func.id in astParser._unfold_symbol_fun_arg:
            return astParser._unfold_symbol_fun_arg[Node.func.id](astParser, Node.args,Node.keywords)
        if Node.func.id in astParser.local_function:
            return body_unfold_call_local_func( astParser ,Node)
        
        raise Exception("unknown function")

    if hasattr(Node.func, 'value'):
        obj = astParser.Unfold_body(Node.func.value)
        #obj = astParser.getInstantByName(Node.func.value.id)
        memFunc = Node.func.attr
        f = getattr(obj,memFunc)

        args = list()
        for x in Node.args:
            args.append(astParser.Unfold_body(x))
        
        gf_type = isFunction()
        set_isFunction(True)
        if len(args) == 0:
            r = f()  # find out how to forward args 
        elif len(Node.args) == 1:
            r = f(args[0])  # find out how to forward args
        elif len(Node.args) == 2:
            r = f(args[0],args[1])  # find out how to forward args
        set_isFunction(gf_type)

        r = v_copy(to_v_object(r))
        vhdl =hdl.impl_function_call(obj, memFunc,[obj]+ args,astParser)
        r.set_vhdl_name(vhdl)
        ret = v_call(memFunc,r, vhdl)
        return ret

    if hasattr(Node.func, 'func'):
        return body_unfold_call(astParser,Node.func)


    raise Exception("Unknown call type")





def body_expr(astParser,Node):
    return    astParser.Unfold_body(Node.value)




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











def body_list(astParser,Node):
    localContext = astParser.Context
    ret = list()
    astParser.Context  = ret
    for x in Node:
        l = astParser.Unfold_body(x)
        ret.append(l)
    astParser.Context =localContext 
    return ret





def body_UnaryOP(astParser,Node):
    ftype = type(Node.op).__name__
    return astParser._Unfold_body[ftype](astParser,Node)




def body_subscript(astParser,Node):
    value = astParser.Unfold_body(Node.value)
    sl  = astParser.Unfold_body(Node.slice)
    return hdl.impl_slice(value, sl,astParser)

def body_index(astParser,Node):
    sl  = astParser.Unfold_body(Node.value)
    return sl 

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




