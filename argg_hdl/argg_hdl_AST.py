import ast
import os
import sys
import inspect
import time



from argg_hdl.argg_hdl_base import *
from argg_hdl.argg_hdl_AST_Classes import * 
from argg_hdl.argg_hdl_v_function import *
from argg_hdl.argg_hdl_v_symbol  import *

def get_function_definition(b_list, name):
    ret = []
    for x in b_list:
        if x.name == name:
            ret.append(x)

    return ret

def checkIfFunctionexists(cl_instant, name, funcArg ):
    for x in cl_instant.__hdl_converter__.MemfunctionCalls:
        if x["name"] != name:
            continue
        
        if not isSameArgs(x["args"] ,funcArg):
            continue
        return True
    
    return False


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

def hasMissingSymbol(FuncArgs):
    for x in FuncArgs:
        if x["symbol"] is None:
            return True
    return False

def GetNewArgList(FunctionName , FunctionArgs,TemplateDescription):

    
    if FunctionName != TemplateDescription["name"]:
        return None
    localArgs = copy.copy(FunctionArgs) #deepcopy
    for x,y in zip(localArgs,TemplateDescription["args"]):
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


class argg_hdl_error:
    def __init__(self,FileName,LineNo,Column,typeName, msg):
        super().__init__()
        self.FileName  = FileName
        self.LineNo    = LineNo
        self.Column    = Column
        self._typeName  = typeName
        self.msg       = msg

    def __str__(self):
        ret = 'File "' + self.FileName + '", line ' +str(self.LineNo) + ", Column: " + str(self.Column) +", type: " + self._typeName + ", msg: " + self.msg
        return ret

    def Show_Error(self):
        with open(self.FileName) as f:
            content =  f.readlines()
        
        ROI = content[max(0,self.LineNo-6 ) : self.LineNo]
        ROI=join_str(ROI)
        ROI = ROI.rstrip()
        s = ' ' * self.Column
        ret = [str(self), ROI, s+"^",s+"| error msg: "+self.msg ]
        return ret 
class xgenAST:

    def __init__(self,sourceFileName):
        
        self.FuncArgs = list()
        self.LocalVar = list()
        self.varScope = list()
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
            "dataType":dataType,
            "rising_edge" : handle_rising_edge,
            "print"       : handle_print,
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
            'Subscript'     : body_subscript,
            "Index"         : body_index,
            'Yield'         : body_unfold_yield,
            "For"           : body_unfold_for,
            "Break"         : body_unfold_Break,
            "Continue"      : body_unfold_Continue
        }
        with open(sourceFileName, "r") as source:
            self.tree = ast.parse(source.read())

        self.ast_v_classes = list(get_subclasses(self.tree.body,['v_class','v_class_master',"v_class_slave", "v_class_trans"]))
        self.ast_v_Entities = list(get_subclasses(self.tree.body,['v_entity']))
        self.ast_v_Entities.extend( list(get_subclasses(self.tree.body,['v_clk_entity'])))
    
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

    def extractArchetectureForEntity(self, ClassInstance, parent):
        setDefaultVarSig(varSig.signal_t)

        ClassName  = type(ClassInstance).__name__
        cl = self.getClassByName(ClassName)
        for f in cl.body:
            if  f.name in self.functionNameVetoList:
                continue

            self.Missing_template = False
            ClassInstance.__hdl_converter__.reset_TemplateMissing(ClassInstance)
            self.reset_buffers()

            self.parent = parent
            self.FuncArgs.append({
                "name":"self",
                "symbol": ClassInstance,
                "ScopeType": InOut_t.InOut_tt
            })
            
            
            
            self.local_function = ClassInstance.__init__.__globals__
            self.Archetecture_vars = ClassInstance.__local_symbols__
            try:
                body = self.Unfold_body(f)  ## get local vars 
            except Exception as inst:
                err_msg = argg_hdl_error(
                    self.sourceFileName,
                    f.lineno, 
                    f.col_offset,
                    ClassName, 
                    "Function Name: " + f.name  +", Unable to Unfold AST, Error In extractArchetectureForEntity: body = self.Unfold_body(f)"
                )
                raise Exception(err_msg,ClassInstance,inst)
            

            if self.Missing_template:
                ClassInstance.__hdl_converter__.FlagFor_TemplateMissing(ClassInstance)
                ClassInstance.__hdl_converter__.MissingTemplate = True
            else:
                proc = v_Arch(
                    body=body,
                    Symbols=self.LocalVar, 
                    Arch_vars=self.Archetecture_vars,
                    ports=ClassInstance.getMember()
                )
                ClassInstance.__processList__.append(proc)

            return self

    def extractFunctionsForEntity(self, ClassInstance, parent):
        ClassName  = type(ClassInstance).__name__
        cl = self.getClassByName(ClassName)
        for f in cl.body:
            
            if  f.name in self.functionNameVetoList:
                continue
            self.parent = parent
            
            self.reset_buffers()
            
            
            
            self.FuncArgs.append(
                {
                    "name":"self",
                    "symbol": ClassInstance,
                    "ScopeType": InOut_t.InOut_tt

                }
            )
            #p=ClassInstance._process1()
            
            #self.local_function = p.__globals__
            self.local_function = ClassInstance.__init__.__globals__

            try:
                body = self.Unfold_body(f)  ## get local vars 
            except Exception as inst:
                err_msg = argg_hdl_error(
                    self.sourceFileName,
                    f.lineno, 
                    f.col_offset,
                    ClassName, 
                    "Function Name: " + f.name  +", Unable to Convert AST to String, Error In extractFunctionsForEntity: body = self.Unfold_body(f)"
                )
                raise Exception(err_msg,ClassInstance,inst)


            

            header =""
            for x in self.LocalVar:
                if x._type == "undef":
                    continue
                header += x.__hdl_converter__._vhdl__DefineSymbol(x, "variable")

            pull =""
            for x in self.LocalVar:
                if x._type == "undef":
                    continue
                pull += x._vhdl__Pull()

            push =""
            for x in self.LocalVar:
                if x._type == "undef":
                    continue
                push += x._vhdl__push()
            
            for x in f.body:
                if type(x).__name__ == "FunctionDef":
                    b = self.Unfold_body(x)
                    body = str(b)  ## unfold function of intressed  
                    break
            
            body =pull +"\n" + body +"\n" + push
            
            proc = v_process(
                body=body, 
                SensitivityList=b.dec[0].get_sensitivity_list(),
                prefix=b.dec[0].get_prefix(), 
                VariableList=header
            )
            ClassInstance.__processList__.append(proc)
            
    
    def extractFunctionsForClass_impl(self, ClassInstance,parent, funcDef, FuncArgs , setDefault = False ):
            self.push_scope("function")
            if hasMissingSymbol(FuncArgs):
                return None
            
            self.reset_buffers()

            ClassName  = type(ClassInstance).__name__

            self.parent = parent
            self.FuncArgs = FuncArgs
            
            
            FuncArgsLocal = copy.copy(FuncArgs)
            varSigSuffix = get_function_varSig_suffix(FuncArgsLocal)




              
            try:
                body = self.Unfold_body(funcDef)
            except Exception as inst:
                err_msg = argg_hdl_error(
                    self.sourceFileName,
                    funcDef.lineno, 
                    funcDef.col_offset,
                    ClassName, 
                    "Function Name: " + funcDef.name  +", Unable to Unfold AST.  Error In extractFunctionsForClass_impl: body = self.Unfold_body(funcDef)"
                )
                raise Exception(err_msg,ClassInstance,inst)
              

            try:
                bodystr= str(body)
            except Exception as inst:
                err_msg = argg_hdl_error(
                    self.sourceFileName,
                    funcDef.lineno, 
                    funcDef.col_offset,
                    ClassName, 
                    "Function Name: " + funcDef.name  +", Unable to Convert AST to String, Error In extractFunctionsForClass_impl: bodystr= str(body)"
                )
                raise Exception(err_msg,ClassInstance,inst)

            #print("----------" , funcDef.name)
            argList = [x["symbol"].__hdl_converter__.to_arglist(x["symbol"], x['name'],ClassName, withDefault = setDefault and  (x["name"] != "self")) for x in FuncArgsLocal]
            ArglistProcedure = join_str(argList,Delimeter="; ")
            

         
            actual_function_name = ClassInstance.__hdl_converter__.function_name_modifier(ClassInstance, funcDef.name, varSigSuffix)


            if "return" in bodystr:
                ArglistProcedure = ArglistProcedure.replace(" in "," ").replace(" out "," ").replace(" inout "," ")
                ret = v_function(
                    name=actual_function_name, 
                    body=bodystr,
                    VariableList=self.get_local_var_def(), 
                    returnType=body.get_type(),
                    argumentList=ArglistProcedure,
                    isFreeFunction=True
                )
            else:
                ret = v_procedure(
                    name=actual_function_name,
                    body=bodystr,
                    VariableList=self.get_local_var_def(), 
                    argumentList=ArglistProcedure,
                    isFreeFunction=True
                )
            self.pop_scope()
            return ret

    def extractArchetectureForClass0(self,ClassInstance,Arc):
        if not (Arc.decorator_list and Arc.decorator_list[0].id == 'architecture') :
            return 
        if not (Arc.name not in [x["name"] for x in ClassInstance.__hdl_converter__.archetecture_list ]):
            return 
        
        arc = self.extractArchetectureForClass(ClassInstance,f)
        
        if not arc:
            return
        
        ClassInstance.__hdl_converter__.archetecture_list.append({
        "name"   : Arc.name,
        "symbol" : arc
        })
            

    def extractArchetectureForClass(self,ClassInstance,Arc):
        ret = None
        primary = ClassInstance.__hdl_converter__.get_primary_object(ClassInstance)
        ClassInstance.__hdl_converter__ = primary.__hdl_converter__
        ClassInstance = copy.deepcopy(ClassInstance)
        self.reset_buffers()
        
        self.FuncArgs.append({
            "name":"self",
            "symbol":  ClassInstance,
            "ScopeType": InOut_t.InOut_tt
        })
            
        self.local_function = ClassInstance.__init__.__globals__
        ClassInstance.__hdl_name__ = "!!SELF!!"


        try:
            body = self.Unfold_body(Arc)  ## get local vars 
        
        except Exception as inst:
            err_msg = argg_hdl_error(
                self.sourceFileName, 
                Arc.lineno, 
                Arc.col_offset, 
                type(ClassInstance).__name__, 
                "FileName: " + Arc.name +", Unable to Unfold AST, Error In extractArchetectureForClass:  body = self.Unfold_body(Arc)"
            )
            raise Exception(err_msg,ClassInstance,inst)
              


        if self.Missing_template:
            ClassInstance.__hdl_converter__.FlagFor_TemplateMissing(
                ClassInstance
            )
            ClassInstance.__hdl_converter__.MissingTemplate = True

        else:
            ret = v_Arch(
                body=body,
                Symbols=self.LocalVar, 
                Arch_vars=self.Archetecture_vars,
                ports=ClassInstance.getMember()
            )

        self.reset_buffers()
       
        return ret

    def get_arglistlocal_extractFunctionsForClass2(self,ClassInstance, cl_body ,ClassInstance_local,parent,temp):
        ArglistLocal = []
        ArglistLocal.append({
            "name":"self",
            "symbol": v_deepcopy(ClassInstance),
            "ScopeType": InOut_t.InOut_tt
        })

        f =  get_function_definition(cl_body,temp["name"])
        if len(f) == 0:
            raise Exception(
                "unable to find function template: ",
                temp["name"],
                ClassInstance
            )
                
        ArglistLocal += list(self.get_func_args_list(f[0]))
        newArglist = GetNewArgList(
            f[0].name, 
            ArglistLocal, 
            temp
        )
        return f,newArglist

    def extractFunctionsForClass2(self,ClassInstance, cl_body ,ClassInstance_local,parent):
        fun_ret = []
        for temp in ClassInstance.__hdl_converter__.MemfunctionCalls:
            if temp["call_func"] is not None:
                continue
                
              
            f,newArglist  = self.get_arglistlocal_extractFunctionsForClass2(ClassInstance, cl_body ,ClassInstance_local,parent,temp)
            

            if newArglist is None:
                continue 
            
            ArglistLocal_length = len(newArglist)
            self.Missing_template = False
            ret = self.extractFunctionsForClass_impl(
                ClassInstance_local, 
                parent, 
                f[0], 
                newArglist , 
                temp["setDefault"]  
            )
            
            if self.Missing_template:
                ClassInstance.__hdl_converter__.MissingTemplate = True
                continue
            
            temp["call_func"] = call_func
            temp["func_args"] = newArglist[0: ArglistLocal_length] #deepcopy
            
            if ret:
                fun_ret.append( ret )
        
        return fun_ret
    #@profile
    def extractFunctionsForClass1a(self,ClassInstance,parent,f ):
        if f.decorator_list and f.decorator_list[0].id == 'architecture' :
            return


        ClassInstance.set_vhdl_name ( "self",True)
        Arglist = []
        Arglist.append({
            "name":"self",
            "symbol": v_deepcopy(ClassInstance),
            "ScopeType": InOut_t.InOut_tt
        })
        Arglist[-1]["symbol"]._Inout  = InOut_t.InOut_tt
        Arglist += list(self.get_func_args_list(f))
        exist = checkIfFunctionexists(ClassInstance,f.name , Arglist)
        if  exist:
            return

        print(str(gTemplateIndent) +'<request_new_template name="'+ str(f.name)+'"/>' )
        

        ClassInstance.__hdl_converter__.MemfunctionCalls.append({
            "name" : f.name,
            "args":  [x["symbol"] for x in   Arglist],
            "self" :v_deepcopy(ClassInstance),
            "call_func" : None,
            "func_args" : None,
            "setDefault" : True
        })

    def extractFunctionsForClass1(self,ClassInstance,parent,cl_body ):
        for f in cl_body:

            if  f.name in self.functionNameVetoList:
                continue


            self.extractArchetectureForClass0(ClassInstance,f)
            self.extractFunctionsForClass1a(ClassInstance,parent,f)

            
    def extractFunctionsForClass(self,ClassInstance,parent ):
        fun_ret = []
        primary = ClassInstance.__hdl_converter__.get_primary_object(ClassInstance)
        ClassInstance.__hdl_converter__ = primary.__hdl_converter__
        ClassInstance.__hdl_converter__.MissingTemplate = False
        ClassName  = type(ClassInstance).__name__
        ClassInstance_local = v_deepcopy(ClassInstance)
        #ClassInstance_local._remove_connections()
        
        cl = self.getClassByName(ClassName)
        try:
            print(str(gTemplateIndent) +'<processing name="'  + str(ClassName) +'" MemfunctionCalls="' +str(len(ClassInstance.__hdl_converter__.MemfunctionCalls)) +'">')
            gTemplateIndent.inc()
            self.extractFunctionsForClass1(ClassInstance,parent,cl.body)
            gTemplateIndent.deinc()
            print(str(gTemplateIndent)+'</processing>')   
        except Exception as inst:
            err_msg = argg_hdl_error(
                self.sourceFileName,
                cl.lineno, 
                cl.col_offset,
                ClassName, 
                "error while processing templates"
            )
            raise Exception(err_msg,ClassInstance,inst)
        finally:
            gTemplateIndent.deinc

        try:
            fun_ret += self.extractFunctionsForClass2( ClassInstance,cl.body,ClassInstance_local,parent)
        except Exception as inst:
            err_msg = argg_hdl_error(
                self.sourceFileName,
                cl.lineno, 
                cl.col_offset,
                ClassName, 
                "error while creating function from template"
            )
            raise Exception(err_msg,ClassInstance,inst)
        
 
        return fun_ret

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





    def get_func_args(self, funcDef):
        
        ret =[]
        for i in range(len(funcDef.args.args),1,-1):
            if len(funcDef.args.defaults ) >= i-2 +1:
                default = funcDef.args.defaults[i-2]
            else:
                default = None
            ret.append((funcDef.args.args[i-1].arg,default))
        ret.reverse()
        return ret

    def get_func_args_list(self, funcDef):
        ret =[]
    
        for args in self.get_func_args(funcDef): 
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

def get_function_varSig_suffix(func_args):
    varSigSuffix = "_"
    for x in func_args:
        if get_symbol(x)._varSigConst == varSig.signal_t:
            varSigSuffix += "1"
        else:
            varSigSuffix += "0"

    return varSigSuffix


def call_func(obj, name, args, astParser=None,func_args=None):
    varSigSuffix = get_function_varSig_suffix(func_args)
    
    ret = []

    for arg,func_arg  in zip(args,func_args ):
        ys =func_arg["symbol"].__hdl_converter__.extract_conversion_types(func_arg["symbol"])
        for y in ys:
            line = func_arg["name"] + y["suffix"]+ " => " + str(arg.__hdl_name__) + y["suffix"]
            ret.append(line)
            if y["symbol"]._varSigConst ==varSig.signal_t:
                members = y["symbol"].getMember()
                for m in members:
                    if m["symbol"].__writeRead__ == InOut_t.output_t:
                        line = func_arg["name"] + y["suffix"]+"_"+ m["name"] +" => " + arg.__hdl_name__ + y["suffix"]  +"."+m["name"]
                        ret.append(line)
                        #print(line)
            


    actual_function_name = func_args[0]["symbol"].__hdl_converter__.function_name_modifier(func_args[0]["symbol"], name, varSigSuffix)
    ret = join_str(ret, Delimeter=", ", start= actual_function_name +"(" ,end=")")
    #print(ret)
    return ret
