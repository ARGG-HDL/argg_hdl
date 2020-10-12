
import  functools 
import copy
import  argg_hdl.argg_hdl_hdl_converter as  hdl
from argg_hdl.argg_hdl_base import print_cnvt, gTemplateIndent, v_deepcopy
from argg_hdl.ast.argg_hdl_AST_MemFunctionCalls import memFunctionCall, call_func, checkIfFunctionexists, hasMissingSymbol, get_function_varSig_suffix, GetNewArgList
from argg_hdl.ast.argg_hdl_ast_hdl_error import argg_hdl_error,Hanlde_errors
from  argg_hdl.argg_hdl_lib_enums import  getDefaultVarSig ,setDefaultVarSig, varSig, InOut_t
from  argg_hdl.argg_hdl_base_helpers import join_str
from argg_hdl.argg_hdl_v_function import v_procedure, v_function ,v_Arch, v_process
from argg_hdl.argg_hdl_global_settings import sort_archetecture


class AST_entity_converter:


    def __init__(self,  astParser ,ClassInstance, parent):
        self.ClassInstance = ClassInstance
        self.parent = parent
        self.astParser = astParser


    def get_architechtures(self):
        ClassInstance = self.ClassInstance
        parent = self.parent
        setDefaultVarSig(varSig.signal_t)

        ClassName  = type(ClassInstance).__name__
        cl = self.astParser.getClassByName(ClassName)
        for f in cl.body:
            if  f.name in self.astParser.functionNameVetoList:
                continue

            self.astParser.Missing_template = False
            ClassInstance.__hdl_converter__.reset_TemplateMissing(ClassInstance)
            self.astParser.reset_buffers()

            self.astParser.parent = parent
            self.astParser.FuncArgs.append({
                "name":"self",
                "symbol": ClassInstance,
                "ScopeType": InOut_t.InOut_tt
            })
            
            
            
            self.astParser.local_function = ClassInstance.__init__.__globals__

            if sort_archetecture():
                self.astParser.Archetecture_vars = sorted(ClassInstance.__local_symbols__, key=lambda element_: element_["type_name"])
            else:
                self.astParser.Archetecture_vars = ClassInstance.__local_symbols__

            try:
                body = self.astParser.Unfold_body(f)  ## get local vars 
            except Exception as inst:
                err_msg = argg_hdl_error(
                    self.astParser.sourceFileName,
                    f.lineno, 
                    f.col_offset,
                    ClassName, 
                    "Function Name: " + f.name  +", Unable to Unfold AST, Error In extractArchetectureForEntity: body = self.Unfold_body(f)"
                )
                raise Exception(err_msg,ClassInstance,inst)
            

            if self.astParser.Missing_template:
                ClassInstance.__hdl_converter__.FlagFor_TemplateMissing(ClassInstance)
                ClassInstance.__hdl_converter__.MissingTemplate = True
            else:
                proc = v_Arch(
                    body=body,
                    Symbols=self.astParser.LocalVar, 
                    Arch_vars=self.astParser.Archetecture_vars,
                    ports=ClassInstance.getMember()
                )
                ClassInstance.__processList__.append(proc)

            

def extractFunctionsForEntity(astParser, ClassInstance, parent):
    ClassName  = type(ClassInstance).__name__
    cl = astParser.getClassByName(ClassName)
    for f in cl.body:
        
        if  f.name in astParser.functionNameVetoList:
            continue
        astParser.parent = parent
        
        astParser.reset_buffers()
        
        
        
        astParser.FuncArgs.append(
            {
                "name":"self",
                "symbol": ClassInstance,
                "ScopeType": InOut_t.InOut_tt
            }
        )
        #p=ClassInstance._process1()
        
        #self.local_function = p.__globals__
        astParser.local_function = ClassInstance.__init__.__globals__
        try:
            body = astParser.Unfold_body(f)  ## get local vars 
        except Exception as inst:
            err_msg = argg_hdl_error(
                astParser.sourceFileName,
                f.lineno, 
                f.col_offset,
                ClassName, 
                "Function Name: " + f.name  +", Unable to Convert AST to String, Error In extractFunctionsForEntity: body = self.Unfold_body(f)"
            )
            raise Exception(err_msg,ClassInstance,inst)
        
        header =""
        for x in astParser.LocalVar:
            if x._type == "undef":
                continue
            header += x.__hdl_converter__.impl_symbol_instantiation(x, "variable")
        pull =""
        for x in astParser.LocalVar:
            if x._type == "undef":
                continue
            pull += x._vhdl__Pull()
        push =""
        for x in astParser.LocalVar:
            if x._type == "undef":
                continue
            push += x._vhdl__push()
        
        for x in f.body:
            if type(x).__name__ == "FunctionDef":
                b = astParser.Unfold_body(x)
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
         
    
