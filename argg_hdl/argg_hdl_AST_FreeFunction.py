import  functools 
import copy
import  argg_hdl.argg_hdl_hdl_converter as  hdl
from argg_hdl.argg_hdl_base import print_cnvt, gTemplateIndent
from argg_hdl.argg_hdl_AST_MemFunctionCalls import memFunctionCall, call_func, checkIfFunctionexists, hasMissingSymbol, get_function_varSig_suffix, GetNewArgList
from argg_hdl.argg_hdl_ast_hdl_error import argg_hdl_error
from  argg_hdl.argg_hdl_lib_enums import  getDefaultVarSig ,setDefaultVarSig, varSig
from  argg_hdl.argg_hdl_base_helpers import join_str
from argg_hdl.argg_hdl_v_function import v_procedure, v_function

def Hanlde_errors(description=""):

    def decorator_Hanlde_errors(func):
        @functools.wraps(func)
        def wrapper_Hanlde_errors(self, *args, **kwargs):
            try:
                
                gTemplateIndent.inc()
                return func(self, *args, **kwargs)
            except Exception as inst:
                err_msg = argg_hdl_error(
                    self.astParser.sourceFileName,
                    self.Function_Node.cl.lineno, 
                    self.Function_Node.cl.col_offset,
                    self.freeFunction.FuncName, 
                    description
                )
                raise Exception(err_msg,self.freeFunction,inst)
            finally:
                gTemplateIndent.deinc()


        return wrapper_Hanlde_errors
    
    return decorator_Hanlde_errors



class AST_FreeFunction:
    def __init__(self,astParser, freeFunction ,package ):
        self.astParser = astParser
        self.freeFunction = freeFunction
        self.package = package
        self.Function_Node = astParser.getFreeFunctionByName(freeFunction.FuncName)



    @Hanlde_errors( "error while processing templates")
    def __request_function_with_default_arguments__(self):
        Arglist = []
        
        Arglist += list(self.astParser.get_func_args_list(self.Function_Node ,IsFreeFunction = True ))
        exist = checkIfFunctionexists(self.freeFunction, self.freeFunction.FuncName , Arglist)
        if  exist:
            return

        print_cnvt(str(gTemplateIndent) +'<request_new_template name="'+ str(self.freeFunction.FuncName)+'"/>' )
        

        self.freeFunction.__hdl_converter__.MemfunctionCalls.append(
            memFunctionCall(
            name= self.freeFunction.FuncName,
            args= [x["symbol"] for x in   Arglist],
            obj= self.freeFunction,
            call_func = call_func,
            func_args = None,
            setDefault = False,
            varSigIndependent = False
        ))


    def __get_requested_function__list(self):
        for temp in self.freeFunction.__hdl_converter__.MemfunctionCalls:
            if temp.call_func is not None:
                continue

            
            newArglist = GetNewArgList(
                self.freeFunction.FuncName, 
                list(self.astParser.get_func_args_list( self.Function_Node  ,IsFreeFunction =True )), 
                temp
            )
            if newArglist is None:
                continue 

            yield temp, newArglist
            
    @Hanlde_errors("error while creating function from template")
    def __implement_requested_functions__(self):        
        fun_ret = []
        for temp, newArglist in self.__get_requested_function__list():

            
            ArglistLocal_length = len(newArglist)
            self.astParser.Missing_template = False
            ret = self.extractFreeFunctions2_impl(
                newArglist                  
            )
            
            if self.astParser.Missing_template:
                self.freeFunction.__hdl_converter__.MissingTemplate = True
                continue
            
            if ret is None:
                continue

            fun_ret.append( ret )
            temp.call_func = call_func
            temp.func_args = newArglist[0:ArglistLocal_length]
            
        
        return fun_ret


    def extractFreeFunctions2_impl(self, FuncArgs ):
            if hasMissingSymbol(FuncArgs):
                return None
            
            self.astParser.push_scope("function")
            self.astParser.reset_buffers()
            dummy_DefaultVarSig = getDefaultVarSig()
            setDefaultVarSig(varSig.variable_t)



            self.astParser.parent = self.package
            self.astParser.FuncArgs = FuncArgs
            self.astParser.local_function = self.freeFunction.__init__.__globals__

            FuncArgsLocal = copy.copy(FuncArgs)
            
            
            body = self.body_unfold()
            bodystr= self.convert_to_string(body)
            
            ret = self.make_function_or_procedure(
                returnType=body.get_type() , 
                bodystr=bodystr, 
                FuncArgsLocal=FuncArgsLocal
            )


            setDefaultVarSig(dummy_DefaultVarSig)
            self.astParser.pop_scope()
            return ret
    
    def body_unfold(self):
        try:
            body = self.astParser.Unfold_body(self.Function_Node)
            return body
        except Exception as inst:
            err_msg = argg_hdl_error(
                self.astParser.sourceFileName,
                self.Function_Node.lineno, 
                self.Function_Node.col_offset,
                type(self.freeFunction).__name__, 
                "Function Name: " + self.Function_Node.name  +", Unable to Unfold AST.  Error In extractFunctionsForClass_impl: body = self.Unfold_body(funcDef)"
            )

            raise Exception(err_msg,self.package,inst)
        
              
    def convert_to_string(self, body):
        try:
            bodystr= str(body)
            return bodystr
        except Exception as inst:
            err_msg = argg_hdl_error(
                self.astParser.sourceFileName,
                self.Function_Node.lineno, 
                self.Function_Node.col_offset,
                type(self.freeFunction).__name__, 
                "Function Name: " + self.Function_Node.name  +", Unable to Convert AST to String, Error In extractFunctionsForClass_impl: bodystr= str(body)"
            )

            raise Exception(err_msg,self.package,inst)

    def make_function_or_procedure(self, returnType , bodystr, FuncArgsLocal):
        argList = [
            x["symbol"].__hdl_converter__.to_arglist(
                x["symbol"], 
                x['name'],
                type(self.freeFunction).__name__, 
                withDefault = True,
                astParser=self.astParser
            ) 
            for x in FuncArgsLocal
        ]
        ArglistProcedure = join_str(argList,Delimeter="; ")
        actual_function_name = self.freeFunction.__hdl_converter__.function_name_modifier(self.freeFunction, self.freeFunction.FuncName, get_function_varSig_suffix(FuncArgsLocal))

        
        if returnType is not None:
            ArglistProcedure = ArglistProcedure.replace(" in "," ").replace(" out "," ").replace(" inout "," ")
            ret = v_function(
                name=actual_function_name, 
                body=bodystr,
                VariableList=self.astParser.get_local_var_def(), 
                returnType=returnType, #body.get_type(),
                argumentList=ArglistProcedure,
                isFreeFunction=True
            )
            return ret 
            
        ret = v_procedure(
            name=actual_function_name,
            body=bodystr,
            VariableList=self.astParser.get_local_var_def(), 
            argumentList=ArglistProcedure,
            isFreeFunction=True
        )
        
        return ret 

    


    def get_functions(self):
        
  
        primary = hdl.get_primary_object(self.freeFunction)
        self.freeFunction.__hdl_converter__ = primary.__hdl_converter__
        self.freeFunction.__hdl_converter__.MissingTemplate = False

        
        print_cnvt(str(gTemplateIndent) +'<processing name="'  + self.freeFunction.FuncName +'" MemfunctionCalls="' +str(len(self.freeFunction.__hdl_converter__.MemfunctionCalls)) +'">')
        self.__request_function_with_default_arguments__()
        print_cnvt(str(gTemplateIndent)+'</processing>')   


        fun_ret = self.__implement_requested_functions__()
        
        return fun_ret
        