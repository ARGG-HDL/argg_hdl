
from  argg_hdl.argg_hdl_base_helpers import *


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
