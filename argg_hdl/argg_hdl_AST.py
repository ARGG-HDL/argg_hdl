import ast
import os
import sys
import inspect
import time


import debugpy

from argg_hdl.argg_hdl_base import *
from argg_hdl.argg_hdl_v_function import *
from argg_hdl.argg_hdl_v_symbol  import *

from argg_hdl.ast.argg_hdl_AST_Classes import * 
from argg_hdl.ast.argg_hdl_AST_MemFunctionCalls import memFunctionCall, call_func, get_function_varSig_suffix, checkIfFunctionexists, hasMissingSymbol, GetNewArgList
from argg_hdl.ast.argg_hdl_AST_FreeFunction import AST_FreeFunction
from argg_hdl.ast.argg_hdl_AST_member_function_converter import AST_member_function_converter
from argg_hdl.ast.argg_hdl_AST_entity_converter import AST_entity_converter, extractFunctionsForEntity

from argg_hdl.ast.argg_hdl_ast_hdl_error import argg_hdl_error






def check_if_subclasses(BaseNames,baseclasses):
    for b in BaseNames:
        if b  in baseclasses:
            return True
    return False

def get_subclasses(astList,BaseNames):
    for astObj in astList:
        if  type(astObj).__name__ == 'ClassDef':
            baseclasses = [x.id  for x in astObj.bases]
            if  check_if_subclasses(BaseNames,baseclasses):
                yield astObj


def getDecoratorName(decoratorAST):
    if hasattr(decoratorAST,"id"):
        return decoratorAST.id
    
    if hasattr(decoratorAST,"func"):
        return decoratorAST.func.id
    
    raise Exception("name Not found")

def get_function_with_decorater(astList,Decorator):
    for astObj in astList:
        if  type(astObj).__name__ == 'FunctionDef':
            Decorators = [x  for x in astObj.decorator_list if getDecoratorName(x) in Decorator]
            if Decorators:
                yield astObj
      

dataType_ = list()
def dataType(astParser=None, args=None):
    Name = None
    if args:
        Name = args[0]

    if dataType_:
        if Name is None:
            return dataType_[-1]["symbol"]
        
        
        for x in dataType_:
            if x["name"] == Name:
                return x["symbol"]
        raise Exception("unknown data type")

    return v_slv()

def AddDataType(dType,Name=""):
    dataType_.append(
        {
            "name"   : Name,
            "symbol" : copy.deepcopy( dType)
        }
    )





class xgenAST:

    def __init__(self,sourceFileName):
        
        self.FuncArgs = list()
        self.LocalVar = list()
        self.varScope = list()
        self.Function_obj_used_list=list()
        self.Missing_template = False
        self.Archetecture_vars = list()
        self.ContextName = list()
        self.ContextName.append("global")
        self.Context = None
        self.parent = None
        self.sourceFileName =sourceFileName
        self._unfold_argList ={
            "Call" : Unfold_call,
            "Num" : unfold_num,
            "Str" : unfold_Str
        }

        self.functionNameVetoList = [
            "__init__",
            "create",
            '_to_hdl___bool__',
            '_vhdl__getValue',
            "_vhdl__reasign",
            '_connect',
            "_sim_get_value",
            "get_master",
            "get_slave"
        ]

        self.local_function ={}
        self._unfold_symbol_fun_arg={
            "port_in" : port_in_to_vhdl,
            "port_out" : port_out_to_vhdl,
            "variable_port_in" :  variable_port_in_to_vhdl,
            "variable_port_out" : variable_port_out_to_vhdl,
            "v_slv"  : v_slv_to_vhdl,
            "v_sl"  : v_sl_to_vhdl,
            "v_int" : v_int_to_vhdl,
            "v_bool" : v_bool_to_vhdl,
            "v_symbol" : v_symbol_to_vhdl,
            "dataType":dataType,
            "rising_edge" : handle_rising_edge,
            "print"       : handle_print,
            "printf"      : handle_print,
            "v_switch"  : handle_v_switch,
            "v_case"    : handle_v_case,
            "len"       : body_handle_len,
            "end_architecture" : body_end_architecture
        }

        self._Unfold_body={
            "FunctionDef"   : body_unfold_functionDef,
            "Return"        : body_unfold_return,
            "Compare"       : body_unfold_Compare,
            "Attribute"     : body_unfold_Attribute,
            "Num"           : body_unfold_Num,
            "Assign"        : body_unfold_assign,
            "Name"          : body_unfold_Name,
            "Call"          : body_unfold_call,
            "Expr"          : body_expr,
            "BinOp"         : body_BinOP,
            "LShift"        : body_LShift,
            'RShift'        : body_RShift,
            "BitOr"         : body_bitOr,
            "Str"           : body_unfold_str,
            'NameConstant'  : body_Named_constant,
            "Constant"      : body_Constant,
            "If"            : body_if,
            "list"          : body_list,
            "BoolOp"        : body_BoolOp,
            "UnaryOp"       : body_UnaryOP,
            "Add"           : body_add,
            "Sub"           : body_sub,
            "Mult"          : body_multi,
            'Subscript'     : body_subscript,
            "Index"         : body_index,
            'Yield'         : body_unfold_yield,
            "For"           : body_unfold_for,
            "Break"         : body_unfold_Break,
            "Continue"      : body_unfold_Continue,
            'Slice'         : body_unfold_slice,
            'BitAnd'        : body_unfold_BitAnd,
            'USub'          : body_unfol_USub,
            'Not'           : body_unfol_Not

        }
        with open(sourceFileName, "r") as source:
            self.tree = ast.parse(source.read())

        self.ast_v_classes = list(get_subclasses(self.tree.body,['v_class','v_class_master',"v_class_slave", "v_class_trans","v_record","v_data_record"]))
        self.ast_v_Entities = list(get_subclasses(self.tree.body,['v_entity']))
        self.ast_v_Entities.extend( list(get_subclasses(self.tree.body,['v_clk_entity'])))
        self.free_functions =  list(get_function_with_decorater(self.tree.body,['hdl_export'])) 
    
    def AddStatementBefore(self,Statement):
        if self.Context is not None:
            self.Context.append(Statement)

    def push_scope(self,NewContextName=None):
        
        if not NewContextName:
            NewContextName = self.ContextName[-1]
        self.ContextName.append(NewContextName)

        self.varScope.append(self.LocalVar)
        self.LocalVar = list()

    def get_scope_name(self):
        return self.ContextName[-1]


    def pop_scope(self):
        self.LocalVar =  self.varScope[-1]
        del self.varScope[-1]
        del self.ContextName[-1]
        
    def try_get_variable(self,name):
        for x in self.LocalVar:
            if name == x.__hdl_name__:
                return x


        for x in self.FuncArgs:
            if name in x["name"]:
                return x["symbol"]
        return None

    def get_variable(self,name, Node):
        
        x  = self.try_get_variable(name)
        if x:
            return x

        raise Exception(Node_line_col_2_str(self, Node)+"Unable to find variable: " + name)

    def get_function_arg_inout_type(self,obj):
        for x in self.Function_obj_used_list:
            if str(x["symbol"]) == str(obj):
                return x["readWrite"]

        
        return InOut_t.Unset_t

    def getClassByName(self,ClassName):
        for x in self.ast_v_classes:
            if x.name == ClassName:
                return x
        for x in self.ast_v_Entities:
            if x.name == ClassName:
                return x

        raise Exception("unable to find v_class '" + ClassName +"' in source '"+ self.sourceFileName+"'")


    def get_local_var_def(self):
        ret =""
        for x in self.LocalVar:
            ret += x.__hdl_converter__._vhdl__DefineSymbol(x)
        
        return ret
    def reset_buffers(self):
        self.local_function ={}
        self.FuncArgs = list()
        self.LocalVar = list()
        self.Archetecture_vars =[]
        self.Function_obj_used_list = []

    def find_in_Function_obj_used_list(self,obj):
        for x in self.Function_obj_used_list:
            if x["symbol"] is obj:
                return x

        return None
    def add_child(self,parent, obj):
        
        x = self.find_in_Function_obj_used_list(obj)
        if x is not None:
            x["parent"] = parent
            return

        self.Function_obj_used_list.append({
            "symbol"    : obj,
            "parent"    : parent,
            "readWrite" : None
        })

    def get_parant(self, obj):
        x = self.find_in_Function_obj_used_list(obj)
        if x:
            return self.get_parant(x["parent"])
        
        return obj

    def add_read(self, obj):
        x = self.find_in_Function_obj_used_list(obj)
        if x is not None:
            x["readWrite"] = Inout_add_input(x["readWrite"])
            return

        self.Function_obj_used_list.append({
            "symbol"    : obj,
            "parent"    : None,
            "readWrite" : Inout_add_input()
        })

    def add_write(self, obj):
        x = self.find_in_Function_obj_used_list(obj)
        if x is not None:
            x["readWrite"] = Inout_add_output(x["readWrite"])
            return

        self.Function_obj_used_list.append({
            "symbol"    : obj,
            "parent"    : None,
            "readWrite" : Inout_add_output()
        })

    def extractArchetectureForEntity(self, ClassInstance, parent):
        entity_conv=AST_entity_converter(self, ClassInstance, parent)
        entity_conv.get_architechtures()


    def extractFunctionsForEntity(self, ClassInstance, parent):
        extractFunctionsForEntity(self, ClassInstance, parent)
        


    
            
    def extractFunctionsForClass(self,ClassInstance,parent ):
        mem_functions = AST_member_function_converter(ClassInstance,self, parent)
        ret = mem_functions.get_functions()
        return ret
     
    def extractFreeFunctions(self, freeFunction ,package ):
        free = AST_FreeFunction(self, freeFunction ,package)
        ret = free.get_functions()
        return ret


    def getFreeFunctionByName(self,FreeFunctionName):
        for x in self.free_functions:
            if x.name == FreeFunctionName:
                return x
        raise Exception("Function not found: ", FreeFunctionName)

    
    def Unfold_body(self,FuncDef):
        try:
            ftype = type(FuncDef).__name__
            return self._Unfold_body[ftype](self,FuncDef)
        except Exception as inst:
            flat_list = flatten_list([FuncDef])
            er = []
            for x in flat_list:
                er.append(argg_hdl_error(self.sourceFileName,x.lineno, x.col_offset,type(x).__name__, "Error In unfolding"))

            raise Exception(er,FuncDef, inst)
        

    def unfold_argList(self,x):
        x_type = type(x).__name__
        if x_type in self._unfold_argList:
            return self._unfold_argList[x_type](self, x)
        return self._Unfold_body[x_type](self,x)

    def getInstantByName(self,SymbolName):
        if issubclass(type(SymbolName),argg_hdl_base):
            return SymbolName


        for x in self.LocalVar:
            if x.__hdl_name__ == SymbolName:
                return x

        for x in self.varScope:
            index = -1
            for y in x:
                index = index + 1
                if y.__hdl_name__ == SymbolName:
                    self.LocalVar.append(y)
                    return y

        for x in self.FuncArgs:
            if x["name"] == SymbolName:
                return x["symbol"]


        for x in self.Archetecture_vars:
            if x["name"] == SymbolName:
                self.LocalVar.append(x["symbol"])
                return x["symbol"]

        if self.parent:
            ret = self.parent.getInstantByName(SymbolName)
            if ret:
                return ret 
                

        if SymbolName in self.local_function: 
            return self.local_function[SymbolName]

        


        raise Exception("Unable to find symbol", SymbolName, "\nAvalible Symbols\n",self.FuncArgs)





    def get_func_args(self, funcDef,IsFreeFunction = False ):
        
        endPoint = 1
        if IsFreeFunction:
            endPoint = 0

        ret =[]
        funcDef.args.args.reverse()
        funcDef.args.defaults.reverse()
        for i in range(0, len(funcDef.args.args)- endPoint):
            if len(funcDef.args.defaults ) > i:
                default = funcDef.args.defaults[i]
            else:
                default = None
            ret.append((funcDef.args.args[i].arg,default))
        ret.reverse()
        funcDef.args.args.reverse()
        funcDef.args.defaults.reverse()
        return ret

    def get_func_args_list(self, funcDef, IsFreeFunction = False):
        ret =[]
    
        for args in self.get_func_args(funcDef,IsFreeFunction): 
            inArg = None
            if args[1] is not None:
                inArg = self.unfold_argList(args[1])
                inArg = to_v_object(inArg)
                inArg.set_vhdl_name(args[0],True)
            ret.append({
                    "name": args[0],
                    "symbol": inArg
                })
        return ret




