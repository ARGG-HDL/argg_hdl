from enum import Enum 
import copy
import  inspect 
import argg_hdl.argg_hdl_core_pack_generator as core_gen
import argg_hdl.argg_hdl_debug_vis as debug_vis
from argg_hdl.argg_hdl_AST_MemFunctionCalls import memFunctionCall
from  argg_hdl.argg_hdl_base_helpers import *
from  argg_hdl.argg_hdl_lib_enums import *
from argg_hdl.argg_hdl_global_settings import *
import  functools 
import  argg_hdl.argg_hdl_hdl_converter as  hdl

from argg_hdl.argg_hdl_type_info import typeInfo

from typing import Sequence, TypeVar
T = TypeVar('T', bound='Copyable')

def architecture(func):
    def wrap(self,*args, **kwargs): 
        func(self,*args, **kwargs) 
    return wrap

def end_architecture():
    add_symbols_to_entiy()

def hdl_export(description=None):
    funcrec = inspect.stack()
    def decorator_hdl_export(func):

        @functools.wraps(func)
        def wrapper_hdl_export(*args, **kwargs):
            return func(*args, **kwargs)
        wrapper_hdl_export.funcrec = funcrec[1]
        wrapper_hdl_export.description = description
        return wrapper_hdl_export
    return decorator_hdl_export


def hdl_constructor(func):
    def wrap(self,*args, **kwargs):
        self.add_args(*args, **kwargs)
        func(self, *args, **kwargs)
    return wrap

def isInList(check_list, obj):
    for x in  check_list:
        if x is obj:
            return True

    return False


def remove_duplications(In_list):
    ret=[]
    for x in  In_list:
        if not isInList(ret, x):
            ret.append(x)

    return ret


def isInList_type(check_list, obj):
    for x in  check_list:
        if type(x).__name__ == "list":
            if isInList_type(x,obj):
                return True 
        elif x.get_type() ==  obj.get_type():
            return True

    return False


def remove_duplications_types(In_list):
    ret=[]
    for x in  In_list:
        if x is None:
            continue
        if not isInList_type(ret, x):
            ret.append(x)
    return ret




def isComment(s):
    while s.strip():
        b_ind = s.find("--")
        if b_ind == -1:
            break
        e_ind = s.find("\n",b_ind)
        s = s[:b_ind] + s[e_ind:]

    if s.strip():
        return False

    return True


def hdl_string_fix_semicolons(hdl_str):
    hdl_str = hdl_str.split(";")
    ret = ""
    for x in hdl_str:
        if not x.strip():
            continue 
        if isComment(x):
            ret += x 
            continue
        
        ret += x + ";"


    #hdl_str = [x for x in hdl_str if x.strip()]
    #hdl_str= join_str(hdl_str,Delimeter=";",end=";")
    return ret

def file_get_contents(filename):
    with open(filename) as f:
        return f.read().strip()

def file_set_content(filename,content):
    with open(filename,'w', newline="") as f:
        f.write(content)

def raise_if(condition,errorMessage):
    if condition:
        raise Exception(errorMessage)


def get_value_or_default(value,default):
    if value is None:
        return default

    return value

def get_fileName_of_object_def(obj):
    funcrec = inspect.stack()
    FileName = ""
    for x in funcrec[1:]:
        f_locals = x.frame.f_locals
        
        objectFound = False
        for y in f_locals:
            if f_locals[y] is obj:
                objectFound = True

        if not objectFound:
            return FileName
        FileName =   x.filename
    return ""
    
def get_variables_from_function_in_callstack(FunctionName):
    funcrec = inspect.stack()
    for x in funcrec:
            #print (x.function)
        if x.function == FunctionName:
            f_locals = x.frame.f_locals
            return f_locals
    
    raise Exception("unable to find Function in callstack. Function Name", FunctionName)


def add_symbols_to_entiy():
    f_locals = get_variables_from_function_in_callstack("architecture")
    for y in f_locals:
        if y != "self" and issubclass(type(f_locals[y]), argg_hdl_base0):
            f_locals["self"]._add_symbol(y,f_locals[y])
            



        







gHDL_objectList = []
gHDL_objectList_primary = []

def g_global_reset():
    gHDL_objectList.clear()
    gHDL_objectList_primary.clear()
    gStatus["isConverting2VHDL"] = False
    gStatus["isProcess"]  =  False
    gStatus["isPrimaryConnection"]= True
    gStatus["MakeGraph"] = True
    gStatus["saveUnfinishFiles"] = False

    gTemplateIndent.reset()



def make_unique_includes(incs,exclude=None):
    sp = incs.split(";")
    sp  = [x.strip() for x in sp]
    sp = sorted(set(sp))
    ret = ""
    for x in sp:
        if len(x)==0:
            continue
        if exclude and "work."+exclude+".all" in x:
            continue
        ret += x+";\n"
    return ret




def unfold_errors(error):
    er_list = []
    er_list += [error.args[0]]

    if type(error.args[-1]).__name__ == "Exception":
        er_list += unfold_errors(error.args[-1])
    else:
        for x in error.args[1:]:
            er_list.append(str(x))
        if type(error.args[0][0]).__name__ == "argg_hdl_error":
            er_list.append(error.args[0][0].Show_Error())

    return er_list
    

def convert_to_hdl(Obj, FolderPath):
    s = isConverting2VHDL()
    set_isConverting2VHDL(True)
    try:
        core_gen.generate_files_in_folder(FolderPath)
        return hdl.convert_all(Obj,  FolderPath)
    except Exception as inst:
        er_list  =  unfold_errors(inst)
        ret = join_str(er_list, Delimeter="\n")
        print_cnvt(ret)
    finally:
        set_isConverting2VHDL(s)








class hdl_converter_base:
    __VHDL__OPS_to2str= {
        "Gt": ">",
        "Eq" : "=",
        "GtE" :">=",
        "LtE" :"<=",
        "Lt"  :"<"
    }

    get_dependency_objects_index = 0

    

    def __init__(self):
        self.MemfunctionCalls=[]
        self.IsConverted = False
        self.MissingTemplate = False
        self.extractedTypes = []






    def get_dependency_objects(self, obj, dep_list):
        self.get_dependency_objects_index += 1
        if self.get_dependency_objects_index > 10:
            self.get_dependency_objects_index -= 1
            return []

        dep_list += [getattr(obj, x[0]) for x in obj.__dict__.items() if issubclass(type(getattr(obj, x[0])),argg_hdl_base) and getattr(obj, x[0])._issubclass_("v_class")]

        
        for x in hdl.get_MemfunctionCalls(obj):
            dep_list += x.args

        dep_list = flatten_list(dep_list)
        ret     = remove_duplications(dep_list)
        ret     = remove_duplications_types(ret)
        old_length = 0
        newLength = len(ret)
        while newLength > old_length:
            old_length = newLength
            ret1 = []
            for x in ret:
                if x is obj:
                    continue
                if x is None:
                    continue
                if isInList_type(ret1, x):
                    continue
                ret1.append(hdl.get_dependency_objects(x,ret))
            
            ret1.append(obj)
            ret1 = flatten_list(ret1)
            ret1 = remove_duplications(ret1)
            ret1 = remove_duplications_types(ret1)
            ret = ret1
            newLength = len(ret)
        
        self.get_dependency_objects_index -= 1
        return ret
        
    def ops2str(self, ops):
        return  self.__VHDL__OPS_to2str[ops]

    def get_MemfunctionCalls(self,obj):
        primary = hdl.get_primary_object(obj)
        return primary.__hdl_converter__.MemfunctionCalls
    

    def FlagFor_TemplateMissing(self, obj):
        primary = hdl.get_primary_object(obj)
        primary.__hdl_converter__.MissingTemplate  = True

    def reset_TemplateMissing(self, obj):
        primary = hdl.get_primary_object(obj)
        primary.__hdl_converter__.MissingTemplate  = False  

    def isTemplateMissing(self,obj):
        primary = hdl.get_primary_object(obj)
        return primary.__hdl_converter__.MissingTemplate  

    def IsSucessfullConverted(self,obj):
        if hdl.isTemplateMissing(obj):
            return False
        return self.IsConverted

    def prepare_for_conversion(self,obj):
        for m in obj.__dict__:
            if not issubclass(type(m),argg_hdl_base0):
                continue 
            hdl.prepare_for_conversion(m)


    def convert_all_packages(self, obj, ouputFolder,x,FilesDone):
        if x.__abstract_type_info__.vetoHDLConversion:
            return 

        packetName =  hdl.get_packet_file_name(x)
        if packetName not in FilesDone:
            print_cnvt(str(gTemplateIndent)+ '<package_conversion name="'+type(x).__name__ +'">')
            gTemplateIndent.inc()
            hdl.prepare_for_conversion(x)
            hdl.reset_TemplateMissing(x)
            packet = hdl.get_packet_file_content(x)
            if packet and not (x.__hdl_converter__.MissingTemplate and not saveUnfinishedFiles()):
                file_set_content(ouputFolder+"/" +packetName,packet)
            FilesDone.append(packetName)
            if x.__hdl_converter__.MissingTemplate:
                print_cnvt(str(gTemplateIndent)+'<status ="failed">')
            else:
                print_cnvt(str(gTemplateIndent)+'<status ="sucess">')
            gTemplateIndent.deinc()
            print_cnvt(str(gTemplateIndent)+ '</package_conversion>')
        
    def convert_all_entities(self, obj, ouputFolder,x,FilesDone):
        entiyFileName =  hdl.get_entity_file_name(x)
        if entiyFileName not in FilesDone:
            print_cnvt(str(gTemplateIndent)+'<entity_conversion name="'+type(x).__name__ +'">')
            gTemplateIndent.inc()
            hdl.prepare_for_conversion(x)
            hdl.reset_TemplateMissing(x)
            try:
                entity_content = hdl.get_enity_file_content(x)
            except Exception as inst:
                raise Exception(["Error in entity Converion:\nEntityFileName: "+ entiyFileName], x,inst)
            if entity_content and not (x.__hdl_converter__.MissingTemplate and not saveUnfinishedFiles()):
                file_set_content(ouputFolder+"/" +entiyFileName,entity_content)
            FilesDone.append(entiyFileName)
            if x.__hdl_converter__.MissingTemplate:
                print_cnvt(str(gTemplateIndent)+'<status ="failed">')
            else:
                print_cnvt(str(gTemplateIndent)+'<status ="sucess">')
            gTemplateIndent.deinc()
            print_cnvt(str(gTemplateIndent)+"</entity_conversion>")
            #print_cnvt("processing")

    def convert_all_impl(self, obj, ouputFolder, FilesDone):
        FilesDone.clear()
        for x in gHDL_objectList:
            hdl.prepare_for_conversion(x)

        for x in gHDL_objectList:
            
            if hdl.IsSucessfullConverted(x):
                continue
            
            self.convert_all_packages(obj, ouputFolder,x,FilesDone)

            self.convert_all_entities(obj, ouputFolder,x,FilesDone)
            x.__hdl_converter__.IsConverted = True


    def convert_all(self, obj, ouputFolder):

        counter = 0
        
        FilesDone = ['']
        while len(FilesDone) > 0:
            counter += 1
            if counter > 10:
                raise Exception("unable to convert ")
           
            print_cnvt("<!--=======================-->")
            print_cnvt(str(gTemplateIndent)+ '<Converting Index="'+str(counter) +'">')
            gTemplateIndent.inc()
            self.convert_all_impl(obj, ouputFolder, FilesDone)
            gTemplateIndent.deinc()
            print_cnvt(str(gTemplateIndent)+ '</Converting>')

    def get_primary_object(self,obj):
        obj_packetName =  hdl.get_packet_file_name(obj)
        obj_entiyFileName =  hdl.get_entity_file_name(obj)
        i = 0 

        for x in gHDL_objectList_primary:
            if obj_packetName ==  x["packetName"] and obj_entiyFileName == x["entiyFileName"] and isinstance(obj, type(x["symbol"])): 
                return x["symbol"]

        for x in gHDL_objectList:
            i +=1 
            packetName =  hdl.get_packet_file_name(x)
            entiyFileName =  hdl.get_entity_file_name(x)
            if obj_packetName ==  packetName and obj_entiyFileName == entiyFileName and isinstance(obj, type(x)): 
                #print_cnvt(i)
                gHDL_objectList_primary.append({
                    "packetName"    : obj_packetName,
                    "entiyFileName" : obj_entiyFileName,
                    "symbol"            : x
                })
                return x

        gHDL_objectList.append(obj)

        gHDL_objectList_primary.append({
                    "packetName"    : obj_packetName,
                    "entiyFileName" : obj_entiyFileName,
                    "symbol"            : obj
        })
        return obj

    def get_packet_file_name(self, obj):
        return ""

    def get_packet_file_content(self, obj):
        return ""

    def get_enity_file_content(self, obj):
        return ""

    def get_entity_file_name(self, obj):
        return ""

    def get_type_simple(self,obj):
        return type(obj).__name__

    def get_constructor(self,obj):
        return hdl.get_type_simple(obj)+"_ctr(" +value(obj)+")"

    def parse_file(self,obj):
        return ""

    def includes(self,obj, name,parent):
        return ""

    def recordMember(self,obj, name,parent,Inout=None):
        return ""

    def recordMemberDefault(self, obj,name,parent,Inout=None):
        return "" 

    def getHeader(self,obj, name,parent):
        return ""
    def getFuncArg(self,obj,name,parent):
        return ""

    def getBody(self,obj, name,parent):
        return ""

    def _vhdl_make_port(self, obj, name):
        ret =[]
        objName = str(obj)
        ret.append(name + " => " + objName)
        return  ret


    def _vhdl_get_attribute(self,obj, attName):
        return str(obj) + "." +str(attName)

    def _vhdl_slice(self,obj, sl,astParser=None):
        raise Exception("Not implemented")

    
    def _vhdl__compare(self,obj, ops, rhs, astParser =None):
        return str(obj) + " " + hdl.ops2str(obj,ops)+" " + str(rhs)

    def _vhdl__add(self,obj,args):
        return str(obj) + " + " + str(args)
    
    def _vhdl__Sub(self,obj,args):
        return str(obj) + " - " + str(args)

    def _vhdl__multi(self,obj,args):
        return str(obj) + " * " + str(args)
        
    def _to_hdl___bool__(self,obj, astParser):
        obj._add_input()
        astParser.add_read(obj)
        return "to_bool(" + str(obj) + ") "

    def _vhdl__BitAnd(self,obj,rhs,astParser):
        raise Exception("not Implemented")
        

    def function_name_modifier(self,obj,name, varSigSuffix):
        if name == "__bool__":
            return "to_bool"
        if name == "__len__":
            return "length"
        if name == "__lshift__":
            return "set_value" + varSigSuffix+"_lshift"
        if name == "__rshift__":
            return "get_value" + varSigSuffix+"_rshift"
        return name + varSigSuffix

    def _vhdl__getValue(self,obj, ReturnToObj=None,astParser=None):

        astParser.add_read(obj)
        obj._add_input()
        return obj

    def _vhdl__reasign_type(self, obj ):
        return obj

    def _vhdl__reasign(self, obj, rhs, astParser=None,context_str=None):
        asOp = hdl.get_assiment_op(obj)    
        return str(obj) +asOp +  str(rhs)

    def _vhdl__reasign_rshift_(self, obj, rhs, astParser=None,context_str=None):
        return hdl._vhdl__reasign(rhs, obj,astParser,context_str)

    def get_get_call_member_function(self, obj, name, args):
        args = [x.get_symbol() for x in args ]

 
        for x  in obj.__hdl_converter__.MemfunctionCalls:
            if x.name != name:
                continue
            if not x.isSameArgs(args):
                continue
            return x
 
        x =  memFunctionCall(
            name= name,
            args= args,
            obj= obj,
            call_func = None,
            func_args = None,
            setDefault = False,
            varSigIndependent = False
        )
        obj.__hdl_converter__.MemfunctionCalls.append(x)
        obj.IsConverted = False
        return x

    def _vhdl__call_member_func(self, obj, name, args, astParser=None):
        
        primary = hdl.get_primary_object(obj)
        obj.__hdl_converter__ = primary.__hdl_converter__
        
        
        call_obj = hdl.get_get_call_member_function(obj, name, args)
        ret = call_obj.HDL_Call(astParser, args, obj)
        return ret




    

    def _vhdl__DefineSymbol(self,obj, VarSymb="variable"):
        print_cnvt("_vhdl__DefineSymbol is deprecated")
        return VarSymb +" " +str(obj) + " : " +obj._type +" := " + obj._type+"_null;\n"
        #return " -- No Generic symbol definition for object " + self.getName()

    def get_architecture_header(self, obj):
        if obj._Inout != InOut_t.Internal_t:
            return ""
        
        if obj._varSigConst != varSig.signal_t or obj._varSigConst != varSig.signal_t:
            return ""

        VarSymb = get_varSig(obj._varSigConst)

        return VarSymb +" " +str(obj) + " : " +obj._type +" := " + obj._type+"_null;\n"
        
    def get_architecture_body(self, obj):
        return ""

    def get_packet_definition(self, obj):
        return ""

    def get_entity_definition(self, obj):
        return ""

    def get_port_list(self,obj):
        return ""

    def get_process_header(self,obj):
        if obj._Inout != InOut_t.Internal_t:
            return ""
        
        if obj._varSigConst != varSig.variable_t:
            return ""

        VarSymb = get_varSig(obj._varSigConst)

        return VarSymb +" " +str(obj) + " : " +obj._type +" := " + obj.DefaultValue +";\n"

    def get_free_symbols(self,obj,name,parent_list=[]):
        return []

    def _vhdl__Pull(self,obj):
        return ""

    def _vhdl__push(self,obj):
        return ""

    def get_assiment_op(self, obj):
        varSigConst = obj._varSigConst
        raise_if(varSigConst== varSig.const_t, "cannot asign to constant")

        if varSigConst== varSig.signal_t:
            asOp = " <= "
        elif varSigConst== varSig.variable_t:
            asOp = " := "
        else: 
            asOp = " := "

        return asOp

    def get_Inout(self,obj,parent):
        inOut = obj._Inout
        if inOut == InOut_t.Default_t:
            return parent._Inout

        if parent._Inout == InOut_t.input_t or parent._Inout == InOut_t.Slave_t :
            inOut =InoutFlip(inOut)
        
        return inOut
        


    def InOut_t2str2(self, inOut):

        if inOut == InOut_t.input_t:
            return " in "
        
        if inOut == InOut_t.output_t:
            return " out "
        
        if inOut == InOut_t.InOut_tt:
            return " inout "
        
        return " in "
        inOut = obj.__writeRead__
        if inOut == InOut_t.input_t:
            return " in "
        
        if inOut == InOut_t.output_t:
            return " out "
        
        if inOut == InOut_t.InOut_tt:
            return " inout "
        
        raise Exception("unkown Inout type",inOut)

    def InOut_t2str3(self, obj, parent):
        inOut = obj._Inout
        if parent._Inout == InOut_t.input_t or parent._Inout == InOut_t.Slave_t :
            inOut =InoutFlip(inOut)

        if inOut == InOut_t.Default_t:
            inOut = parent._Inout 


        return self.InOut_t2str2(inOut)

    def InOut_t2str(self, obj):
        inOut = obj._Inout
        if inOut == InOut_t.input_t:
            return " in "
        
        if inOut == InOut_t.output_t:
            return " out "
        
        if inOut == InOut_t.InOut_tt:
            return " inout "
        
        inOut = obj.__writeRead__
        if inOut == InOut_t.input_t:
            return " in "
        
        if inOut == InOut_t.output_t:
            return " out "
        
        if inOut == InOut_t.InOut_tt:
            return " inout "
        
        raise Exception("unkown Inout type",inOut)

    def get_default_value(self,obj):
        return obj._type + "_null"


    def extract_conversion_types(self, obj, exclude_class_type=None,filter_inout=None):
        if filter_inout and obj._Inout != filter_inout: 
            return []
        return [{ "suffix":"", "symbol": obj}]

    def get_Name_array(self,obj):
        return hdl.get_type_simple(obj)+"_a"

    def length(self,obj):
        return "length(" +str(obj)+")"

    def to_arglist(self,obj, name,parent,withDefault = False,astParser=None):
        raise Exception("not implemented for class: ", type(obj).__name__)

    def get_inout_type_recursive(self, obj):
        if  obj._Inout != InOut_t.Internal_t:
            return obj._Inout
        return obj.__writeRead__  

    def Has_pushpull_function(self,obj, pushpull):
        return False
    
    def get_HDL_name(self, obj, parent,suffix):
        return parent.__hdl_name__ + suffix


class argg_hdl_base0:
    def __init__(self):
        super().__init__()
        self.__abstract_type_info__ = typeInfo()
        
        if isRunning():
            return 
        if not isConverting2VHDL() :
            gHDL_objectList.append(self)
        if MakeGraph() :
            debug_vis.append(self)

        
        self.__hdl_converter__ = hdl_converter_base()

        self.__Driver__ = None
        self.__Driver_Is_SubConnection__ = False
        self.__receiver__ = []
        self.__srcFilePath__ = get_fileName_of_object_def(self)
        self.__hdl_useDefault_value__ = False


    @property
    def __isInst__(self):
        return self.__abstract_type_info__.__isInst__

    @__isInst__.setter
    def __isInst__(self, value):
        #print("setter of __isInst__ called")
        self.__abstract_type_info__.__isInst__ = value

    @property
    def __isFreeType__(self):
        return self.__abstract_type_info__.__isFreeType__

    @__isFreeType__.setter
    def __isFreeType__(self, value):
        #print("setter of __isFreeType__ called")
        self.__abstract_type_info__.__isFreeType__ = value

    @property
    def _Inout(self):
        return self.__abstract_type_info__._Inout
     
    @_Inout.setter
    def _Inout(self, value):
        #print("setter of _Inout called")
        self.__abstract_type_info__._Inout = value
    
    
    @property
    def _varSigConst(self):
        if hasattr(self, '__abstract_type_info__'):
            return self.__abstract_type_info__._varSigConst
        
        return varSig.runtime_variable_t

    @_varSigConst.setter
    def _varSigConst(self, value):
        #print("setter of _varSigConst called")
        if hasattr(self, '__abstract_type_info__'):
            self.__abstract_type_info__._varSigConst = value


    @property
    def __writeRead__(self):
         return self.__abstract_type_info__.__writeRead__

    @__writeRead__.setter
    def __writeRead__(self, value):
        #print("setter of _varSigConst called")
        self.__abstract_type_info__.__writeRead__ = value

    def _set_to_sub_connection(self):
        self.__Driver_Is_SubConnection__ = True

    def _remove_connections(self):
        self.__Driver__ = None
        self.__Driver_Is_SubConnection__ = False
        self.__receiver__ = []
        xs = self.getMember()
        for x in xs:
            x["symbol"]._remove_connections()

    def getMember(self,InOut_Filter=None, VaribleSignalFilter = None):
        return []

    def get_symbol(self):
        return self

    def DriverIsProcess(self):
        if type(self.__Driver__).__name__ == "str":
            return self.__Driver__ == "process"
        return False

    def _sim_get_new_storage(self):
        pass    

    def set_simulation_param(self,module, name,writer):
        pass
   
    def _sim_start_simulation(self):
        pass

    def _sim_stop_simulation(self):
        pass

    def _sim_set_push_pull(self, Pull_list, Push_list):
        if hasattr(self, "_onPull"):
            Pull_list.append(getattr(self, '_onPull'))

        if hasattr(self, "_onPush"):
            Push_list.append(getattr(self, '_onPush'))

    def js_dump(self):
        return debug_vis.js_dump()

    def _sim_append_update_list(self,up):
        raise Exception("update not implemented")

    def _get_Stream_input(self):
        raise Exception("update not implemented")

    def _get_Stream_output(self):
        raise Exception("update not implemented")
    
    def _instantiate_(self):
        self.__isInst__ = True
        return self
    
    def _un_instantiate_(self, Name = ""):
        self.__isInst__ = False
        if Name:
            self.set_vhdl_name(Name,True)
        return self
    
    def _issubclass_(self,test):
        return "argg_hdl_base0" == test
    def _remove_drivers(self):
        self.__Driver__ = None

    def set_vhdl_name(self,name,Overwrite = False):
        raise Exception("update not implemented")                

    def _add_input(self):
        pass
    def _add_output(self):
        pass
    def _add_used(self):
        pass

    def __rshift__(self, rhs):
        rhs << self
        
class argg_hdl_base(argg_hdl_base0):

    def __init__(self):
        super().__init__()
        if isRunning():
            return 
        self._Inout         = InOut_t.Internal_t
        self.__writeRead__  = InOut_t.Internal_t

    def _add_input(self):
        if self.__writeRead__ == InOut_t.Internal_t:
            self.__writeRead__ = InOut_t.input_t
        elif self.__writeRead__ == InOut_t.output_t:
            self.__writeRead__ = InOut_t.InOut_tt
        elif self.__writeRead__ == InOut_t.Used_t:
            self.__writeRead__ = InOut_t.input_t

    def _add_output(self):
        if self.__writeRead__ == InOut_t.Internal_t:
            self.__writeRead__ = InOut_t.output_t
        elif self.__writeRead__ == InOut_t.input_t:
            self.__writeRead__ = InOut_t.InOut_tt
        elif self.__writeRead__ == InOut_t.Used_t:
            self.__writeRead__ = InOut_t.output_t

    def _add_used(self):
        if self.__writeRead__ == InOut_t.Internal_t:
            self.__writeRead__ = InOut_t.Used_t
        elif self.__writeRead__ == InOut_t.Unset_t:
            self.__writeRead__ = InOut_t.Used_t

    def flipInout(self):
        pass
    def resetInout(self):
        pass
    def getName(self):
        return type(self).__name__


    
    def set_varSigConst(self, varSigConst):
        raise Exception("not implemented for class: ", type(self).__name__)

    def get_vhdl_name(self,Inout):
        return None
        
    def isInOutType(self,Inout):
        return False
        



    def _issubclass_(self,test):
        if super()._issubclass_(test):
            return True
        return "argg_hdl_base" == test

   


    def _sim_get_value(self):
        raise Exception("not implemented")
    



def value(Input):
    if issubclass(type(Input), argg_hdl_base):
        return Input._sim_get_value()
    
    if type(Input).__name__ == "v_Num":
        return Input.value

    if hasattr(Input,"get_value"):
        return Input.get_value()

    if type(Input).__name__ == "EnumMeta":
        return Input.value

    if type(type(Input)).__name__ == "EnumMeta":
            return Input.value
            
    return Input



def v_dataObject(symbol: T) ->T:
    ret= copy.deepcopy(symbol)
    ret._sim_get_new_storage()
    ret.__isInst__ = False
    ret.setInout(InOut_t.Internal_t)
    ret._remove_drivers()
    ret.__hdl_useDefault_value__ = False
    return ret
    

def v_variable(symbol: T) ->T:
    ret= copy.deepcopy(symbol)
    ret._sim_get_new_storage()
    ret.__isInst__ = False
    ret.setInout(InOut_t.Internal_t)
    ret.set_varSigConst(varSig.variable_t)
    ret._remove_drivers()
    return ret
    
    
def v_signal(symbol: T) ->T:
    ret= copy.deepcopy(symbol)
    ret._sim_get_new_storage()
    ret.__isInst__ = False
    ret.setInout(InOut_t.Internal_t)
    ret.set_varSigConst(varSig.signal_t)
    ret._remove_drivers()
    return ret

def v_const(symbol: T) ->T:
    ret= copy.deepcopy(symbol)
    ret._sim_get_new_storage()
    ret.__isInst__ = False
    ret.setInout(InOut_t.Internal_t)
    ret.set_varSigConst(varSig.const_t)
    ret._remove_drivers()
    return ret

def port_out(symbol: T) ->T:
    ret= copy.deepcopy(symbol)
    ret._sim_get_new_storage()
    ret.__isInst__ = False
    ret.setInout(InOut_t.output_t)
    ret.set_varSigConst(getDefaultVarSig())
    ret._remove_drivers()
    return ret

def variable_port_out(symbol: T) ->T:
    ret= copy.deepcopy(symbol)
    ret._sim_get_new_storage()
    ret.__isInst__ = False
    ret.setInout(InOut_t.output_t)
    ret.set_varSigConst(varSig.variable_t)
    ret._remove_drivers()
    return ret

def port_in(symbol: T) ->T:
    ret= copy.deepcopy(symbol)
    ret._sim_get_new_storage()
    ret.__isInst__ = False
    ret.setInout(InOut_t.input_t)
    ret.set_varSigConst(getDefaultVarSig())
    ret._remove_drivers()
    return ret

def variable_port_in(symbol: T) ->T:
    ret= copy.deepcopy(symbol)
    ret._sim_get_new_storage()
    ret.__isInst__ = False
    ret.setInout(InOut_t.input_t)
    ret.set_varSigConst(varSig.variable_t)
    ret._remove_drivers()
    return ret




def port_Master(symbol: T) -> T:
    ret = copy.deepcopy(symbol)
    ret._sim_get_new_storage()
    ret.__isInst__ = False
    ret.setInout(InOut_t.Master_t)
    ret.set_varSigConst(getDefaultVarSig())
    ret._remove_drivers()
    return ret


def variable_port_Master(symbol: T) ->T:
    ret = copy.deepcopy(symbol)
    ret._sim_get_new_storage()
    ret.__isInst__ = False
    ret.setInout(InOut_t.Master_t)
    ret.set_varSigConst(varSig.variable_t)
    ret._remove_drivers()
    return ret


def signal_port_Master(symbol: T) ->T:
    ret = copy.deepcopy(symbol)
    ret._sim_get_new_storage()
    ret.__isInst__ = False
    ret.setInout(InOut_t.Master_t)
    ret.set_varSigConst(varSig.signal_t)
    ret._remove_drivers()
    return ret


def port_Stream_Master(symbol: T) ->T:
    ret = port_Master(symbol)
    ret._sim_get_new_storage()
    ret.__isInst__ = False
    funcrec = inspect.stack()[1]

    f_locals = funcrec.frame.f_locals

    raise_if(f_locals["self"]._StreamOut is not None, "the _StreamOut is already set")

    f_locals["self"]._StreamOut = ret
    ret._remove_drivers()
    return ret


def signal_port_Slave(symbol: T) ->T:
    ret = copy.deepcopy(symbol)
    ret._sim_get_new_storage()
    ret.__isInst__ = False
    ret.setInout(InOut_t.Slave_t)
    ret.set_varSigConst(varSig.signal_t)
    ret._remove_drivers()
    return ret


def port_Slave(symbol: T) ->T:
    ret = copy.deepcopy(symbol)
    ret._sim_get_new_storage()
    ret.__isInst__ = False
    ret.setInout(InOut_t.Slave_t)
    ret.set_varSigConst(getDefaultVarSig())
    ret._remove_drivers()
    return ret


def variable_port_Slave(symbol: T) ->T:
    ret = copy.deepcopy(symbol)
    ret._sim_get_new_storage()
    ret.__isInst__ = False
    ret.setInout(InOut_t.Slave_t)
    ret.set_varSigConst(varSig.variable_t)
    ret._remove_drivers()
    return ret


def port_Stream_Slave(symbol: T) ->T:
    ret = port_Slave(symbol)
    ret._sim_get_new_storage()
    ret.__isInst__ = False
    funcrec = inspect.stack()[1]

    f_locals = funcrec.frame.f_locals
    raise_if(f_locals["self"]._StreamIn is not None, "the _StreamIn is already set")

    f_locals["self"]._StreamIn = ret
    ret._remove_drivers()
    return ret


def v_copy(symbol:T, varSig_=None)->T:
    ret = copy.deepcopy(symbol)
    ret._sim_get_new_storage()
    ret.resetInout()
    ret.__isInst__ = False
    ret.__hdl_name__ = None
    ret._remove_drivers()
    if ret._varSigConst== varSig.combined_t:
        pass
    if varSig is None:
        ret.set_varSigConst(getDefaultVarSig())
    return ret


def v_deepcopy(symbol: T) ->T:
    hdl = symbol.__hdl_converter__
    driver = symbol.__Driver__
    receiver = symbol.__receiver__
    symbol.__receiver__ = None
    symbol.__Driver__ = None
    symbol.__hdl_converter__ = None
    ret = copy.deepcopy(symbol)
    symbol.__hdl_converter__ = hdl
    ret.__hdl_converter__ = hdl
    symbol.__Driver__ = driver
    ret.__Driver__ = driver
    symbol.__receiver__ = receiver
    ret.__receiver__ = receiver

    return ret
