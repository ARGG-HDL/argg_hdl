import functools 
import copy
import argg_hdl.argg_hdl_hdl_converter as  hdl
from argg_hdl.argg_hdl_base import print_cnvt, gTemplateIndent, v_deepcopy
from argg_hdl.argg_hdl_lib_enums import  getDefaultVarSig ,setDefaultVarSig, varSig, InOut_t
from argg_hdl.argg_hdl_base_helpers import join_str
from argg_hdl.argg_hdl_v_function import v_procedure, v_function ,v_Arch
from argg_hdl.argg_hdl_global_settings import sort_archetecture

from argg_hdl.ast.argg_hdl_AST_MemFunctionCalls import memFunctionCall, call_func, checkIfFunctionexists, hasMissingSymbol, get_function_varSig_suffix, GetNewArgList
from argg_hdl.ast.argg_hdl_ast_hdl_error import argg_hdl_error,Hanlde_errors

def get_function_definition(b_list, name):
    ret = []
    for x in b_list:
        if x.name == name:
            ret.append(x)

    return ret

class AST_member_function_converter:
    def __init__(self,ClassInstance, astParser ,parent ):

        self.ClassInstance = ClassInstance
        self.ClassName  = type(ClassInstance).__name__
        self.astParser = astParser
        self.class_Node = astParser.getClassByName(self.ClassName )
        self.parent = parent

    def sourceFileName(self):
        return self.astParser.sourceFileName
    
    def lineno(self):
        return self.class_Node.lineno
    
    def col_offset(self):
        return self.class_Node.col_offset

    def Name(self):
        return self.ClassName



    
    def get_architecture_definition(self):
        for f in self.class_Node.body:

            if  f.name in self.astParser.functionNameVetoList:
                continue
            if f.name in self.ClassInstance.__hdl_converter__.functionNameVetoList:
                continue

            if not (f.decorator_list and f.decorator_list[0].id == 'architecture') :
                continue 
            if not (f.name not in [x["name"] for x in  self.ClassInstance.__hdl_converter__.archetecture_list ]):
                continue 
            yield f


    @Hanlde_errors("error while processing class architecture")
    def Extract_architecture(self):

        for arch in self.get_architecture_definition():
            self.extractArchetectureForClass(arch)
            

    def get_architecture_vars(self):
        if sort_archetecture():
            return  sorted(self.ClassInstance.__local_symbols__, key=lambda element_: element_["type_name"])

        return  self.ClassInstance.__local_symbols__   

    def unfold_architecture(self,Arc):
        try:
            body = self.astParser.Unfold_body(Arc)  ## get local vars 
            return body
        except Exception as inst:
            err_msg = argg_hdl_error(
                self.astParser.sourceFileName, 
                Arc.lineno, 
                Arc.col_offset, 
                type(self.ClassInstance).__name__, 
                "FileName: " + Arc.name +", Unable to Unfold AST, Error In extractArchetectureForClass:  body = self.Unfold_body(Arc)"
            )
            raise Exception(err_msg,ClassInstance,inst)

    
    def extractArchetectureForClass(self,Arc):
        ClassInstance = self.ClassInstance
        ret = None
        primary = ClassInstance.__hdl_converter__.get_primary_object(ClassInstance)
        ClassInstance.__hdl_converter__ = primary.__hdl_converter__
        ClassInstance = copy.deepcopy(ClassInstance)
        self.astParser.reset_buffers()
        
        self.astParser.FuncArgs.append({
            "name":"self",
            "symbol":  ClassInstance,
            "ScopeType": InOut_t.InOut_tt
        })
            
        self.astParser.local_function = ClassInstance.__init__.__globals__
        ClassInstance.__hdl_name__ = "!!SELF!!"
        
        self.astParser.Archetecture_vars = self.get_architecture_vars()
        

        body=self.unfold_architecture(Arc)


        if self.astParser.Missing_template:
            hdl.FlagFor_TemplateMissing( ClassInstance  )
      

        else:
            ret = v_Arch(
                body=body,
                Symbols=self.astParser.LocalVar, 
                Arch_vars=self.astParser.Archetecture_vars,
                ports=ClassInstance.getMember()
            )
            self.ClassInstance.__hdl_converter__.archetecture_list.append({
                "name"   : Arc.name,
                "symbol" : ret
            })

        self.astParser.reset_buffers()
       


    def get_function_definitions(self):
        for f in self.class_Node.body:

            if  f.name in self.astParser.functionNameVetoList:
                continue
            if f.name in self.ClassInstance.__hdl_converter__.functionNameVetoList:
                continue
            if f.decorator_list and f.decorator_list[0].id == 'architecture' :
                continue
                
            yield f

    @Hanlde_errors("error while processing templates")
    def __request_function_with_default_arguments__(self):
        for function_node in self.get_function_definitions():
            self.ClassInstance.set_vhdl_name ( "self",True)
            Arglist = []
            Arglist.append({
                "name":"self",
                "symbol": v_deepcopy(self.ClassInstance),
                "ScopeType": InOut_t.InOut_tt
            })
            Arglist[-1]["symbol"]._Inout  = InOut_t.InOut_tt
            Arglist += list(self.astParser.get_func_args_list(function_node))
            exist = checkIfFunctionexists(self.ClassInstance,function_node.name , Arglist)
            if  exist:
                continue

            print_cnvt(str(gTemplateIndent) +'<request_new_template name="'+ str(function_node.name)+'"/>' )
            

            self.ClassInstance.__hdl_converter__.MemfunctionCalls.append(
                memFunctionCall(
                name= function_node.name,
                args= [x["symbol"] for x in   Arglist],
                obj= self.ClassInstance,
                call_func = None,
                func_args = None,
                setDefault = True,
                varSigIndependent = False
            ))

    @Hanlde_errors("error while creating function from template")
    def extractFunctionsForClass2(self):


        fun_ret = []
        for temp in self.ClassInstance.__hdl_converter__.MemfunctionCalls:
            if temp.call_func is not None:
                continue
                
              
            f,newArglist  = self.get_arglistlocal_extractFunctionsForClass2(temp)
            

            if newArglist is None:
                continue 
            
            ArglistLocal_length = len(newArglist)
            self.astParser.Missing_template = False
            ret = self.extractFunctionsForClass_impl(
                f[0], 
                newArglist , 
                temp.setDefault ,
                temp 
            )
            
            if self.astParser.Missing_template:
                self.ClassInstance.__hdl_converter__.MissingTemplate = True
                continue
            
            temp.call_func = call_func
            temp.func_args = newArglist[0: ArglistLocal_length] #deepcopy
            
            if ret:
                fun_ret.append( ret )
        
        return fun_ret        

    
    def get_arglistlocal_extractFunctionsForClass2(self, temp):
        ArglistLocal = []
        ArglistLocal.append({
            "name":"self",
            "symbol": v_deepcopy(self.ClassInstance),
            "ScopeType": InOut_t.InOut_tt
        })

        f =  get_function_definition(self.class_Node.body, temp.name)
        if len(f) == 0:
            raise Exception(
                "unable to find function template: ",
                temp["name"],
                self.ClassInstance
            )
                
        ArglistLocal += list(self.astParser.get_func_args_list(f[0]))
        newArglist = GetNewArgList(
            f[0].name, 
            ArglistLocal, 
            temp
        )
        return f,newArglist     


    def extractFunctionsForClass_impl(self, funcDef, FuncArgs , setDefault = False , MemFunction_template= None ):
        if hasMissingSymbol(FuncArgs):
            return None
        
        self.astParser.push_scope("function")
        self.astParser.reset_buffers()

        self.astParser.parent = self.parent
        self.astParser.FuncArgs = FuncArgs
        
        
        FuncArgsLocal = copy.copy(FuncArgs)
        varSigSuffix = get_function_varSig_suffix(self.astParser.FuncArgs)
        self.astParser.local_function = self.ClassInstance.__init__.__globals__
        
        body = self.unfold_body(funcDef)
 
        
        bodystr= self.convert_to_string(body)
        argList = [
            hdl.to_arglist(
                x["symbol"], 
                x['name'],
                type(self.ClassInstance).__name__, 
                withDefault = setDefault and  (x["name"] != "self"),
                astParser=self.astParser
            ) 
            for x in FuncArgsLocal
        ]
        ArglistProcedure = join_str(argList,Delimeter="; ")
        ret = self.make_function_or_procedure(funcDef.name, body.get_type(), bodystr,FuncArgsLocal, ArglistProcedure, varSigSuffix)
        if body.get_type() is not None:
            MemFunction_template.varSigIndependent = True
        
        self.astParser.pop_scope()
        return ret


    def unfold_body(self,Function_node):
        dummy_DefaultVarSig = getDefaultVarSig()
        setDefaultVarSig(varSig.variable_t)
        try:
            body = self.astParser.Unfold_body(Function_node)
            return body
        except Exception as inst:
            err_msg = argg_hdl_error(
                self.astParser.sourceFileName,
                Function_node.lineno, 
                Function_node.col_offset,
                type(self.ClassInstance).__name__, 
                "Function Name: " + Function_node.name  +", Unable to Unfold AST.  Error In extractFunctionsForClass_impl: body = self.Unfold_body(funcDef)"
            )
            
            raise Exception(err_msg,ClassInstance,inst)
        finally:
            setDefaultVarSig(dummy_DefaultVarSig)

                  
    def convert_to_string(self, body):
        dummy_DefaultVarSig = getDefaultVarSig()
        setDefaultVarSig(varSig.variable_t)
        try:
            bodystr= str(body)
            return bodystr
        except Exception as inst:
            err_msg = argg_hdl_error(
                self.astParser.sourceFileName,
                funcDef.lineno, 
                funcDef.col_offset,
                type(ClassInstance).__name__, 
                "Function Name: " + funcDef.name  +", Unable to Convert AST to String, Error In extractFunctionsForClass_impl: bodystr= str(body)"
            )
        
            raise Exception(err_msg,ClassInstance,inst)
        finally:
            setDefaultVarSig(dummy_DefaultVarSig)

    def make_function_or_procedure(self,functionName, returnType , bodystr, FuncArgsLocal,ArglistProcedure, varSigSuffix):
    
        actual_function_name = hdl.function_name_modifier(self.ClassInstance, functionName, varSigSuffix)
        
        if returnType is not None:
            ArglistProcedure = ArglistProcedure.replace(" in "," ").replace(" out "," ").replace(" inout "," ")
            ret = v_function(
                name=actual_function_name, 
                body=bodystr,
                VariableList=self.astParser.get_local_var_def(), 
                returnType=returnType,
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
        

        primary = self.ClassInstance.__hdl_converter__.get_primary_object(self.ClassInstance)
        self.ClassInstance.__hdl_converter__ = primary.__hdl_converter__
        self.ClassInstance.__hdl_converter__.MissingTemplate = False


        

        print_cnvt(str(gTemplateIndent) +'<processing name="'  + str(self.ClassName ) +'" MemfunctionCalls="' +str(len(self.ClassInstance.__hdl_converter__.MemfunctionCalls)) +'">')
        self.Extract_architecture()
        self.__request_function_with_default_arguments__()
        fun_ret = self.extractFunctionsForClass2()

        print_cnvt(str(gTemplateIndent)+'</processing>')   
 
        return fun_ret
