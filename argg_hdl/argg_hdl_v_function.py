import os
import sys
import inspect
 
from argg_hdl.argg_hdl_base import *
from argg_hdl.argg_hdl__primitive_type_converter  import get_primitive_hdl_converter
#import argg_hdl.argg_hdl_v_Package as argg_pack

class v_procedure_converter(hdl_converter_base):
    def __init__(self):
        super().__init__()
    def getHeader(self, obj,name, parent):
        classDef =""
        if parent is not None and not obj.isFreeFunction:
            classDef = parent.__hdl_converter__.get_self_func_name (parent)

        argumentList = join_str( [classDef, obj.argumentList ],Delimeter="; " ,RemoveEmptyElements = True).strip()
        if obj.name:
            name = obj.name        
        if obj.isEmpty:
            return "-- empty procedure removed. name: '"  + name +"'\n"

        ret = '''  procedure {functionName} ({argumentList});\n'''.format(
                functionName=name,
                argumentList=argumentList

        )
        return ret
    
    
    def getBody(self, obj, name,parent):
        classDef =""
        if parent is not None and not obj.isFreeFunction:
            classDef = parent.__hdl_converter__.get_self_func_name (parent)

        argumentList = join_str( [classDef, obj.argumentList ],Delimeter="; " ,RemoveEmptyElements = True).strip()
        if obj.name:
            name = obj.name      
        if obj.isEmpty:
            return "-- empty procedure removed. name: '"  + name+"'\n"

        ret = '''procedure {functionName} ({argumentList}) is\n  {VariableList} \n  begin \n {body} \nend procedure;\n\n'''.format(
                functionName=name,
                argumentList=argumentList,
                body = obj.body,
                VariableList=obj.VariableList

        )
        return ret

class v_procedure(argg_hdl_base):
    def __init__(self, argumentList="", body="",VariableList="",name=None,IsEmpty=False,isFreeFunction=False):
        super().__init__()
        self.__hdl_converter__ = v_procedure_converter()
        self.argumentList = argumentList

        self.body = body
        self.VariableList=VariableList
        self.name = name
        self.isEmpty = IsEmpty
        self.isFreeFunction =isFreeFunction
    
    def get_type(self):
        return type(self).__name__
    
    def isSubset(self, rhs):#is either the same or is just missing templates
        if self.name != rhs.name:
            return False
        
        if self.argumentList == rhs.argumentList:
            return True

        sl_args = self.argumentList.split(";")
        rhs_args = rhs.argumentList.split(";")
        self_is_subset = False
        rhs_is_subset = False

        if len(sl_args) != len(rhs_args):
            raise Exception("Different Length Not supported")
        for s,r in zip(sl_args,rhs_args):
            ss = s.split(":=")
            rr = r.split(":=")
            if ss[0].strip() != rr[0].strip():
                return False
            if len(ss) < len(rr):
                self_is_subset = True
            
            if len(rr) < len(ss):
                rhs_is_subset = True

           # print(s,r)

        if not self_is_subset and not rhs_is_subset:
            return False
        
        if self_is_subset and not rhs_is_subset:
            return True
        
        
        raise Exception("Unable to Determin which one is the subset")

        




class v_function_converter(hdl_converter_base):
    def __init__(self):
        super().__init__()
    def getHeader(self, obj, name, parent):
        classDef =""
        if parent is not None and not obj.isFreeFunction:
            classDef = parent.__hdl_converter__.get_self_func_name (parent,True)
        argumentList = join_str( [classDef, obj.argumentList ],Delimeter="; " ,RemoveEmptyElements = True ,IgnoreIfEmpty=True).strip()
        if obj.name:
            name = obj.name
        if obj.isEmpty:
            return "-- empty function removed. name: '"  + name+"'\n"

        ret = '''  function {functionName} ({argumentList}) return {returnType};\n'''.format(
                functionName=name,
                argumentList=argumentList,
                returnType=value(obj.returnType)

        )
        return ret
    
    
    def getBody(self, obj, name,parent):
        classDef =""
        if parent is not None and not obj.isFreeFunction:
            classDef = parent.__hdl_converter__.get_self_func_name(parent,True)
        argumentList = join_str( [classDef, obj.argumentList ],Delimeter="; " ,RemoveEmptyElements = True ,IgnoreIfEmpty=True).strip()
        
        if obj.name:
            name = obj.name  
        if obj.isEmpty:
            return "-- empty function removed. name: '"  + name   +"'\n"

        ret = '''function {functionName} ({argumentList}) return {returnType} is\n  {VariableList} \n  begin \n {body} \nend function;\n\n'''.format(
                functionName=name,
                argumentList=argumentList,
                body = obj.body,
                VariableList=obj.VariableList,
                returnType=value(obj.returnType)

        )
        return ret




def remove_signal_and_inouts_specifier(s):
    
    s = " " +s +" "
    s = s.replace(";"," ; ")
    s = s.replace(":="," := ")
    s = s.replace(":"," : ")
    s = s.replace(": ="," := ")
    s = s.replace(" signal "," ")
    s = s.replace(" inout "," ")
    s = s.replace(" in "," ")
    s = s.replace(" out "," ")
    s =' '.join(s.split())

    if len(s)>20:
        s =';\n   '.join(s.split(";"))
        s = "\n   " +s+"\n "
    return s


class v_function(argg_hdl_base):
    def __init__(self,body="", returnType="", argumentList="",VariableList="",name=None,IsEmpty=False,isFreeFunction=False):
        super().__init__()
        self.__hdl_converter__ = v_function_converter()
        self.body = body
        self.returnType = returnType


        self.argumentList = remove_signal_and_inouts_specifier(argumentList)


        self.VariableList=VariableList
        self.name = name
        self.isEmpty = IsEmpty
        self.isFreeFunction =isFreeFunction

    def get_type(self):
        return type(self).__name__

    def __eq__(self, rhs):
        return self.isSubset(rhs)

        
    def isSubset(self,rhs):#is either the same or is just missing templates

        if self.name != rhs.name:
            return False
        
        if self.argumentList == rhs.argumentList:
            return True

        if self.returnType != rhs.returnType:
            return False

        sl_args = self.argumentList.split(";")
        rhs_args = rhs.argumentList.split(";")
        self_is_subset = False
        rhs_is_subset = False

        if len(sl_args) != len(rhs_args):
            raise Exception("Different Length Not supported")
        for s,r in zip(sl_args,rhs_args):
            ss = s.split(":=")
            rr = r.split(":=")
            if ss[0].strip() != rr[0].strip():
                return False
            if len(ss) < len(rr):
                self_is_subset = True
            
            if len(rr) < len(ss):
                rhs_is_subset = True

           # print(s,r)

        if not self_is_subset and not rhs_is_subset:
            return False
        
        if self_is_subset and not rhs_is_subset:
            return True
        
        
        raise Exception("Unable to Determin which one is the subset")

class v_process_converter(hdl_converter_base):
    def __init__(self):
        super().__init__()
    def getBody(self, obj,name,parent):
        ret = "process("+str(obj.SensitivityList)+") is\n" +str(obj.VariableList)+ "\n  begin\n"
        if obj.prefix:
            ret += "  if " + str(obj.prefix) + " then\n"
        ret += obj.body
        if obj.prefix:
            ret += "\n  end if;"
        ret += "\n end process;\n"
        return ret


class v_process(argg_hdl_base):
    def __init__(self,body="", SensitivityList=None,VariableList="",prefix=None,name=None,IsEmpty=False):
        super().__init__()
        self.__hdl_converter__ = v_process_converter()
        self.body = body 
        self.SensitivityList = SensitivityList
        self.VariableList = VariableList
        self.name = name
        self.IsEmpty = IsEmpty
        self.prefix = prefix


    def get_type(self):
        return type(self).__name__


class v_Arch_converter(hdl_converter_base):
    def __init__(self):
        super().__init__()
        

    def includes(self,obj, name,parent):
        inc_str = ""
        for x in obj.Symbols:
            inc_str +=  x.__hdl_converter__.includes(x, x.__hdl_name__,obj)
        
        for x in obj.Arch_vars:
            inc_str +=  hdl.includes(x['symbol'], x['name'],obj)
        return inc_str

    def get_architecture_header(self, obj):
        header = ""
        for x in obj.Symbols:
            if x._type == "undef":
                continue
            header += x.__hdl_converter__.get_architecture_header(x)
        
        for x in obj.Arch_vars:
            header += hdl.get_architecture_header(x['symbol'])    
        return header


    def make_signal_list(self, obj, retList, objList):
        
        for x in objList:
            retList.append(x)
            obj.__hdl_converter__.make_signal_list(
                obj,
                retList, 
                x['symbol'].getMember(VaribleSignalFilter=varSig.signal_t)
            )

  

    def make_signal_connections2(self, obj, objList):
        ret = ""
        for x in objList:
            #print("=====")
            #print(str(x["name"]))

                
            if x['symbol'].__Driver__ is None:
                #print("Has no Driver")
                continue

            if x['symbol'].DriverIsProcess():
                #print("Driver is process")
                continue 
            if  x['symbol'].__Driver__.__hdl_name__ is None:
                #print("Driver has no HDL Name")
                continue 
            if  x['symbol']._varSigConst != varSig.signal_t:
                #print("Is not signal")
                continue
            if  (x['symbol'].__Driver__._varSigConst == varSig.unnamed_const):
                pass
                #print("Driver is unnamed_const")
            if  (x['symbol'].__Driver__._varSigConst == varSig.variable_t):
                #print("Driver is variable_t")
                continue
            if  (x['symbol'].__Driver__._varSigConst == varSig.reference_t):
                #print("Driver is reference_t")
                continue
            if  (x['symbol'].__Driver__._varSigConst == varSig.combined_t):
                #print("Driver is combined_t")
                continue
        
            if not x['symbol'].__hdl_name__:
                #print("Has no HDL Name")
                continue 
            if not list_is_in_list(x['symbol'].__Driver__, objList):
                #print("Driver is not in list")
                if not obj.isEntity:
                    continue
                if  (x['symbol'].__Driver__._varSigConst != varSig.unnamed_const):
                    continue
            if x['symbol'].__Driver_Is_SubConnection__ :
                #print("Is sub connection")
                continue

            if x['symbol'].__isFreeType__ :
                #print("Is sub connection")
                continue
            #print("Connecting " +str(x['name']) )
            ret += x['symbol'].__hdl_converter__._vhdl__reasign(x['symbol'],x['symbol'].__Driver__,context_str = "archetecture")  +";\n  "

        return ret
    def get_architecture_body(self, obj):
        body = ""  
        body += str(obj.body)
        for x in obj.Symbols:
            if x._type == "undef":
                continue
            line = x.__hdl_converter__.get_architecture_body(x) 
            if line.strip():
                body += "\n  " +line+";\n  "
        
        for x in obj.Arch_vars:
            line = x['symbol'].__hdl_converter__.get_architecture_body(x['symbol'])
            if line.strip():
                body += "\n  " + line  +";\n  "
        
        retList =[]
        obj.__hdl_converter__.make_signal_list(obj,retList,  obj.ports)
        obj.__hdl_converter__.make_signal_list(obj,retList,  obj.Arch_vars)
        retlist2 = list_make_unque(retList)
        conections = obj.__hdl_converter__.make_signal_connections2(obj, retlist2)
        #print("====================")
        #print(conections)
        #print("--------------------")
        body += conections
        #body +=obj.__hdl_converter__.make_signal_connections(obj, obj.Arch_vars)
 
        return body


    def getHeader(self, obj, name, parent):
        print_cnvt("getHeader is dep")
        return ""

    def getBody(self,obj, name,parent):
        print_cnvt("getHeader is dep")
        return ""

class v_Arch(argg_hdl_base):
    def __init__(self,body, Symbols,Arch_vars,ports):
        super().__init__()
        self.body = body 
        self.Symbols = Symbols
        self.Arch_vars = Arch_vars
        self.__hdl_converter__ = v_Arch_converter()
        self.ports = ports
        self.name = "arc"
        self.isEntity = False
        
    def get_type(self):
        return type(self).__name__


def list_is_in_list(obj, ret):
    for y in ret:
        if obj is y["symbol"]:
            return True
    return False

def list_make_unque(objList):
    ret = []
    for x in objList:
        if not list_is_in_list(x["symbol"],ret):
            ret.append(x)

    return ret


def is_element_of(obj, class_obj_list):
    for class_obj in class_obj_list:
        mem = class_obj.getMember()
        for m in mem:
            if obj is m["symbol"]:
                return True

    return False




class v_free_function_template(argg_hdl_base):
    def __init__(self,funcrec,FuncName):
        super().__init__()
        self.__hdl_converter__ = get_primitive_hdl_converter(v_free_function_template.__name__)()
        self.funcrec = funcrec
        self.FuncName = FuncName
        self.__srcFilePath__ = self.funcrec.filename
        
    def get_type(self):
        return type(self).__name__


    def _issubclass_(self,test):
        if super()._issubclass_(test):
            return True
        return "v_free_function_template" == test