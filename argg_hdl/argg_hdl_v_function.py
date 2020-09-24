import os
import sys
import inspect
 
from argg_hdl.argg_hdl_base import *
from argg_hdl.argg_hdl__primitive_type_converter  import get_primitive_hdl_converter
#import argg_hdl.argg_hdl_v_Package as argg_pack
from argg_hdl.converter.argg_hdl_hdl_converter_base import hdl_converter_base


class v_procedure(argg_hdl_base):
    def __init__(self, argumentList="", body="",VariableList="",name=None,IsEmpty=False,isFreeFunction=False):
        super().__init__()
        self.__hdl_converter__ =get_primitive_hdl_converter("v_procedure" )() 
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
        self.__hdl_converter__ =get_primitive_hdl_converter("v_function" )() 
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



class v_process(argg_hdl_base):
    def __init__(self,body="", SensitivityList=None,VariableList="",prefix=None,name=None,IsEmpty=False):
        super().__init__()
        self.__hdl_converter__  =get_primitive_hdl_converter("v_process" )() 
        self.body = body 
        self.SensitivityList = SensitivityList
        self.VariableList = VariableList
        self.name = name
        self.IsEmpty = IsEmpty
        self.prefix = prefix


    def get_type(self):
        return type(self).__name__



class v_Arch(argg_hdl_base):
    def __init__(self,body, Symbols,Arch_vars,ports):
        super().__init__()
        self.body = body 
        self.Symbols = Symbols
        self.Arch_vars = Arch_vars
        self.__hdl_converter__ = get_primitive_hdl_converter("v_Arch" )() 
        self.ports = ports
        self.name = "arc"
        self.isEntity = False
        
    def get_type(self):
        return type(self).__name__







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