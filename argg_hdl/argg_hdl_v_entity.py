import  functools 

import os,sys,inspect


from argg_hdl.argg_hdl_base import *
from argg_hdl.argg_hdl_v_symbol import *
from argg_hdl.argg_hdl_v_entity_list import *
from argg_hdl.argg_hdl_AST import *





def process():
    def decorator_processd(func):
        @functools.wraps(func)
        def wrapper_process(getSymb=None):
            return func()
        localVarSig = getDefaultVarSig()

        setDefaultVarSig(varSig.variable_t)
        func()
        setDefaultVarSig(localVarSig)
        add_symbols_to_entiy()

        return wrapper_process
    return decorator_processd



def timed():
    def decorator_timed(func):
        @functools.wraps(func)
        def wrapper_timed(getSymb=None):
            return func()

        gsimulation.timmed_process.append(func)
        return wrapper_timed
    return decorator_timed

def v_create(entity):
    return entity._instantiate_()

class wait_for():
    def __init__(self,time,unit="ns"):
        self.time =time 
        self.unit = unit

    def get_time(self):
        return self.time

    def __str__(self):
        return " " + str(self.time) +" " + self.unit



            
def addPullsPushes_from_closure(Pull_list, Push_list, closure):
    if closure == None:
        return
    for x in closure:
        y = x.cell_contents
        if issubclass(type(y), argg_hdl_base0):
            y._sim_set_push_pull(Pull_list, Push_list)
            



def combinational():
    def decorator_combinational(func):
        @functools.wraps(func)
        def wrapper_combinational():
            return func()

        for symb in func.__closure__:
            symbol = symb.cell_contents
            symbol._sim_append_update_list(wrapper_combinational)
        return wrapper_combinational
    return decorator_combinational

def v_switch(default_value, v_cases):
    for c in v_cases:
        if c["pred"]:
            return c["value"]

    return default_value

def v_case(pred,value):
    ret = {
        "pred" : pred,
        "value" : value 
    }
    return ret

def run_list(functionList):
    for x in functionList:
        x()


def rising_edge(symbol):
    def decorator_rising_edge(func):
        Pull_list = []
        Push_list = []
        @functools.wraps(func)
        def wrapper_rising_edge(getSymb=None):
            if value(symbol) == 1:
                run_list(Pull_list)
                func()
                run_list(Push_list)

        
        addPullsPushes_from_closure(Pull_list,Push_list ,func.__closure__)
        symbol.__update__list_process__.append(wrapper_rising_edge)
        return wrapper_rising_edge
    return decorator_rising_edge

gport_veto__ =[
            "_StreamOut",
            "_StreamIn"
        ]

def v_entity_getMember(entity):
        ret = list()
        for x in entity.__dict__.items():
            if x[0] in gport_veto__:
                continue

            t = getattr(entity, x[0])
            if issubclass(type(t),argg_hdl_base):
                ret.append({
                        "name": x[0],
                        "symbol": t
                    })

        ret=sorted(ret, key=lambda element_: element_["name"])
        return ret

def v_entity_getMember_expand(entity):
        ret = list()
        for x in entity.__dict__.items():
            if x in gport_veto__:
                continue
            t = getattr(entity, x[0])
            if t._issubclass_("v_class"):
                ret.append({
                        "name": x[0],
                        "symbol": t
                    })
            elif t._issubclass_("argg_hdl_base"):
                ret.append({
                        "name": x[0],
                        "symbol": t
                    })
        
        ret=sorted(ret, key=lambda element_: element_["name"])
        return ret

        


class v_entity_converter(hdl_converter_base):
    def __init__(self):
        super().__init__()
        self.astTree = None

    def get_entity_file_name(self, obj):
        return type(obj).__name__+".vhd"

    def get_enity_file_content(self, obj):
        s = isConverting2VHDL()
        set_isConverting2VHDL(True)
        
        obj._un_instantiate_()
        obj.__hdl_converter__.MissingTemplate = False
        obj.__processList__ = []
        
        astparser = obj.__hdl_converter__.parse_file(obj)
        
        ret = "-- XGEN: Autogenerated File\n\n"
        ret += obj.__hdl_converter__.includes(obj, None, obj)
        ret += "\n\n"
        
        ret += obj.__hdl_converter__.get_entity_definition(obj)
        
        if astparser.Missing_template == True:
                obj.__hdl_converter__.FlagFor_TemplateMissing(obj)
                obj.__hdl_converter__.MissingTemplate = True
                print(str(gTemplateIndent)+'<Failed_to_convert name="' + type(obj).__name__ +'"/>')

        obj._instantiate_()
        set_isConverting2VHDL(s)
        return ret




    def parse_file(self,obj):
        if obj.__srcFilePath__:
            self.astTree = xgenAST(obj.__srcFilePath__)
            return self.astTree.extractArchetectureForEntity(obj,None)

        
    def _vhdl_get_attribute(self,obj, attName):
        if obj.__hdl_name__:
            return obj.__hdl_name__ +"_"+ attName
        
        return attName

    def get_archhitecture(self,obj):

        ret = "architecture rtl of "+ obj._name +" is\n\n"

        ret +=  obj.__hdl_converter__.get_architecture_header_def(obj)
        ret += "\nbegin\n"
        ret +=  obj.__hdl_converter__.get_architecture_body_def(obj)
        ret += "\nend architecture;\n"
        return ret 

    def get_architecture_header_def(self, obj):
        if obj.__hdl_name__:
            name = obj.__hdl_name__
        else :
            name = obj._name
        ret = "--------------------------"+ name  +"-----------------\n"
        members= obj.__hdl_converter__.getMember(obj)
        
        for x in members:
            sym = x["symbol"]
            symName = obj.__hdl_converter__._vhdl_get_attribute(obj,x["name"])
            sym.__hdl_name__ = symName
            
            ret +=  sym.__hdl_converter__.get_architecture_header(sym)


        for x in obj.__processList__:
            ret += x.__hdl_converter__.get_architecture_header(x)

        ret += "-------------------------- end "+ name  +"-----------------\n"
        return ret 


    def get_architecture_header(self, obj):
        if obj.__hdl_name__:
            name = obj.__hdl_name__
        else :
            name = obj._name
        ret = "--------------------------"+ name  +"-----------------\n"
        members= obj.__hdl_converter__.getMember(obj)
        
        for x in members:
            sym = x["symbol"]
            if sym._Inout ==InOut_t.Internal_t:
                continue
            symName = obj.__hdl_converter__._vhdl_get_attribute(obj,x["name"])
            sym.__hdl_name__ = symName
            
            ret +=  sym.__hdl_converter__.get_architecture_header(sym)

        ret += "-------------------------- end "+ name  +"-----------------\n"
        return ret 


    def get_architecture_body(self, obj):
        content = []

        for x in v_entity_getMember(obj):
            if x["symbol"]._Inout ==InOut_t.Internal_t:
                continue
            if not x["symbol"].__hdl_name__:
                x["symbol"].set_vhdl_name(str(obj.__hdl_name__)+"_"+ x["name"])

            content += x["symbol"].__hdl_converter__._vhdl_make_port(x["symbol"], x["name"] )


        start = str(obj.__hdl_name__) +" : entity work." + obj._name+" port map (\n    "
        ret=join_str(content,start=start ,end="\n  )",Delimeter=",\n    ")
        return ret
 

    def get_architecture_body_def(self, obj):
        ret = ""
        for x in obj.__processList__:
            ret += x.__hdl_converter__.get_architecture_body(x)
        return ret 



    def getMember(self, obj):
        return v_entity_getMember(obj)
    
    def includes(self,obj, name,parent):
        bufffer = ""
        members= obj.__hdl_converter__.getMember(obj)
        for x in members:
            bufffer += x["symbol"].__hdl_converter__.includes(x["symbol"],x["name"],None)

        for x in obj.__processList__:
            bufffer += x.__hdl_converter__.includes(x,"",None)


        ret = make_unique_includes(bufffer)
        return ret

    def get_declaration(self,obj):
        portdef=[]
        
        for x in obj.__hdl_converter__.getMember(obj):
            sym = x["symbol"]
            sym.__hdl_name__ = x["name"]
            portdef += sym.__hdl_converter__.get_port_list(sym)

      
        ret = "entity " + obj._name + " is \n" 
        ret+=join_str(portdef,start="  port(\n    " ,end="\n  );\n",Delimeter=";\n    ",IgnoreIfEmpty=True)
        ret += "end entity;\n\n"
        return ret

    def get_definition(self, obj):
    
        if obj.__isInst__==True:
            obj._un_instantiate_()
        ret = ""

        ret += "\n\n"
        ret += obj.__hdl_converter__.get_declaration(obj)
        ret += "\n\n"
        ret += obj.__hdl_converter__.get_archhitecture(obj)
        return ret

    def get_process_header(self,obj):
        return ""
        

    def get_entity_definition(self, obj):
        ret = obj.__hdl_converter__.get_definition(obj)
        return ret.strip()

class v_entity(argg_hdl_base0):
    def __init__(self):
        super().__init__()

        self.__hdl_converter__= v_entity_converter()
        setDefaultVarSig(varSig.signal_t)
        name = type(self).__name__
        self._name = name
        #self.__srcFilePath__ = srcFileName
        self.__processList__ = list()
        self._Inout = InOut_t.Internal_t
        self.__hdl_name__ = None
        self._type = "entity"
        self.__local_symbols__ = list()
        self._StreamOut = None
        self._StreamIn  = None

        
    def getMember(self,InOut_Filter=None, VaribleSignalFilter = None):
        ret = list()
        for x in self.__dict__.items():
            t = getattr(self, x[0])
            if not issubclass(type(t),argg_hdl_base) :
                continue 
            if not t.isInOutType(InOut_Filter):
                continue
            
            if not t.isVarSigType(VaribleSignalFilter):
                continue

            ret.append({
                        "name": x[0],
                        "symbol": t
                    })

        ret =sorted(ret, key=lambda element_: element_["name"])
        return ret


    def __or__(self,rhs):

        
        rhs_StreamIn = rhs._get_Stream_input()
        self_StreamOut = self._get_Stream_output()
                
        ret = v_entity_list()


        ret.append(self)
        ret.append(rhs)

        rhs_StreamIn << self_StreamOut
        return ret
        
    def set_simulation_param(self,module, name,writer):
        mem = v_entity_getMember(self)
        for x in mem:
            x["symbol"].set_simulation_param(module +"."+ name, x["name"],writer)

        local_symbols =sorted(self.__local_symbols__, key=lambda element_: element_["name"])
        for x in local_symbols:
            x["symbol"].set_simulation_param(module +"."+ name, x["name"],writer)


    def _add_symbol(self, name,symb):
        for x in self.__local_symbols__:
            if symb is x["symbol"]:
                return

        self.__local_symbols__.append(
            {
                "name" : name,
                "symbol" : symb
            }
        )


    def _instantiate_(self):
        if self.__isInst__ == True:
            return self
            
        mem = v_entity_getMember(self)
        for x in mem:
            self.__dict__[x["name"]]._instantiate_()
        
        self.__isInst__ = True
        return self

    def _un_instantiate_(self, Name = ""):
        if self.__isInst__ == False:
            return self
        

        self.set_vhdl_name(Name, True)
        mem = v_entity_getMember(self)
        for x in mem:
            self.__dict__[x["name"]]._un_instantiate_(x["name"])

        
        self.__isInst__ = False
        return self



    def _sim_append_update_list(self,up):
        pass

    def set_vhdl_name(self,name, Overwrite = False):
        if self.__hdl_name__ and self.__hdl_name__ != name and Overwrite == False:
            raise Exception("double Conversion to vhdl")
        else:
            self.__hdl_name__ = name



    def _get_Stream_input(self):
        if self._StreamIn == None:
            raise Exception("Input stream not defined")
        return  self._StreamIn

    def _get_Stream_output(self):
        if self._StreamOut == None:
            raise Exception("output stream not defined")
        return self._StreamOut


    def _issubclass_(self,test):
        if super()._issubclass_(test):
            return True
        return "v_entity" == test
        
class v_clk_entity(v_entity):
    def __init__(self,clk=None):
        super().__init__()
        self.clk    =  port_in(v_sl())
        if clk != None:
            self.clk <<  clk

    def _issubclass_(self,test):
        if super()._issubclass_(test):
            return True
        return "v_clk_entity" == test