
from  argg_hdl.argg_hdl_base_helpers import *
from argg_hdl.argg_hdl_global_settings import print_cnvt
from  argg_hdl.argg_hdl_lib_enums import varSig, InOut_t
import argg_hdl.argg_hdl_hdl_converter as hdl
import copy

class memFunctionCall:
    def __init__(self,name,args,obj, call_func = None,func_args = None,setDefault = False,varSigIndependent = False):
            self.name = name
            self.args = args
            self.self = obj
            self.call_func = call_func
            self.func_args = func_args
            self.setDefault = setDefault
            self.varSigIndependent = varSigIndependent

    def isSameArgs(self,args2):
        args1 = self.args
        if not self.setDefault and  len(args1) != len(args2):
            return False
        for arg1,arg2 in zip(args1,args2):
            if get_symbol(arg1) is None:
                return False
            if get_symbol(arg2) is None:
                return False
            if get_type(arg1) != get_type( arg2):
                return False

            if self.varSigIndependent  == False \
                and \
            get_symbol(arg1)._varSigConst != varSig.unnamed_const \
                and \
            get_symbol(arg2)._varSigConst != varSig.unnamed_const \
                and \
            get_symbol(arg1)._varSigConst != get_symbol(arg2)._varSigConst:
                return False
        return True  


    def HDL_Call(self, astParser, args, obj):
        
        args_str = [str(x.get_type()) for x in args]
        args_str=join_str(args_str, Delimeter=", ")
        
        
        if self.call_func is None:
            print_cnvt(str(gTemplateIndent)+'<Missing_Template function="' + str(self.name) +'" args="' +args_str+'" />' )
            obj.__hdl_converter__.MissingTemplate=True
            astParser.Missing_template = True
            ret = "$$missing Template$$"
            return ret


        print_cnvt(str(gTemplateIndent)+'<use_template function ="' + str(self.name)  +'" args="' +args_str+'" />'  )
        return self.call_func(obj, self.name, args, astParser, self.func_args)

def hasMissingSymbol(FuncArgs):
    for x in FuncArgs:
        if x["symbol"] is None:
            return True
    return False


def checkIfFunctionexists(cl_instant, name, funcArg ):
    for x in cl_instant.__hdl_converter__.MemfunctionCalls:
        if x.name != name:
            continue
        
        if not x.isSameArgs(funcArg):
            continue
        return True
    
    return False


def get_function_varSig_suffix(func_args):
    varSigSuffix = "_"
    for x in func_args:
        if get_symbol(x)._varSigConst == varSig.signal_t:
            varSigSuffix += "1"
        else:
            varSigSuffix += "0"

    return varSigSuffix

def call_func(obj, name, args, astParser=None,func_args=None):
  
    ret = []

    for arg,func_arg  in zip(args,func_args ):
        ret += hdl.make_function_variable_assignment( func_arg["symbol"], func_arg ,arg )


    varSigSuffix = get_function_varSig_suffix(func_args)
    actual_function_name = func_args[0]["symbol"].__hdl_converter__.function_name_modifier(func_args[0]["symbol"], name, varSigSuffix)
    ret = join_str(ret, Delimeter=", ", start= actual_function_name +"(" ,end=")")
    #print_cnvt(ret)
    return ret



def GetNewArgList(FunctionName , FunctionArgs,TemplateDescription):

    
    if FunctionName != TemplateDescription.name:
        return None
    localArgs = copy.copy(FunctionArgs) #deepcopy
    for x,y in zip(localArgs,TemplateDescription.args):
        if y is None:
            return None  
        if x["symbol"] is None or x["symbol"]._type != y._type or x['symbol']._varSigConst != y._varSigConst:
            #y._Inout =  x["symbol"]._Inout
            y.set_vhdl_name(x["name"],True)
            
            x["symbol"] = copy.deepcopy(y)
            x["symbol"].__writeRead__  = InOut_t.Internal_t
            x["symbol"]._Inout  = InOut_t.Internal_t
            mem = x["symbol"].getMember()
            for m in mem:
                m["symbol"].__writeRead__  = InOut_t.Internal_t
                m["symbol"]._Inout  = InOut_t.Internal_t
    return localArgs
