import os
import sys
import inspect


from argg_hdl.argg_hdl_base import *
from argg_hdl.argg_hdl_v_function import *
from argg_hdl.argg_hdl_v_entity_list import *
from argg_hdl.argg_hdl_simulation import *
import argg_hdl.argg_hdl_v_Package as argg_pack
import  argg_hdl.converter.vhdl_v_class_helpers as  vc_helper

import  argg_hdl.argg_hdl_hdl_converter as  hdl

from  argg_hdl.argg_hdl_object_name_maker import  make_object_name
from argg_hdl.argg_hdl_object_factory import add_constructor




class v_class(argg_hdl_base):

    def __init__(self,Name=None,varSigConst=None):
        super().__init__()
        self.__hdl_converter__ = get_primitive_hdl_converter("v_class" )() 
        Name = get_value_or_default( Name , type(self).__name__)


        self._type = Name
        self.__v_classType__ = v_classType_t.transition_t 


        self.__vectorPush__ = False
        self.__vectorPull__ = False

        self.__hdl_useDefault_value__ = True
        self.__hdl_name__ =None
        self.__Driver__ = None
        self.__local_symbols__ = list()

        
        if not varSigConst:
            varSigConst = getDefaultVarSig()
        self._varSigConst = varSigConst

        self.__inout_register__ = {}
   
   
    def _add_symbol(self, name,symb):
        for x in self.__local_symbols__:
            if symb is x["symbol"]:
                return

        type_name = name

            
        self.__local_symbols__.append(
            {
                "name" : name,
                "symbol" : symb,
                "type_name" : type_name
            }
        )

    def set_vhdl_name(self,name, Overwrite = False):
        if self.__hdl_name__ and self.__hdl_name__ != name and not Overwrite:
            raise Exception("double Conversion to vhdl")
        
        self.__hdl_name__ = name

        

        

        if self._varSigConst == varSig.variable_t:
            mem = self.getMember()
            for x in mem:
                x["symbol"].set_vhdl_name(name+"."+x["name"],Overwrite)
        else:
            xs = hdl.extract_conversion_types(self, exclude_class_type= v_classType_t.transition_t,)
            for x in xs:
                mem = x["symbol"].getMember()
                for m in mem:
                    m["symbol"].set_vhdl_name(name+x["suffix"]+"."+m["name"],Overwrite)



    def _sim_append_update_list(self,up):
        for x  in self.getMember():
            x["symbol"]._sim_append_update_list(up)


    def _sim_get_value(self):
        return self


    def getName(self):
        return self._type

    def get_type(self):
        return self._type

    def __repr__(self):
        
        mem = self.getMember()
        mem = [ x["name"] +"="+ repr(x["symbol"]) for x in mem]
        ret =  join_str(mem, start="[",end="]",Delimeter=", ")
            
        return ret
    def get_vhdl_name(self,Inout=None):
        if Inout is None:
            return str(self.__hdl_name__)
        
        if self.__v_classType__ == v_classType_t.Slave_t:
            Inout = InoutFlip(Inout)

        if Inout== InOut_t.input_t:
            return vc_helper.append_hdl_name(str(self.__hdl_name__), "_s2m")
        
        if Inout== InOut_t.output_t:
            return vc_helper.append_hdl_name(str(self.__hdl_name__), "_m2s")
        
        return None



    def getType(self,Inout=None,varSigType=None):

        if Inout == InOut_t.input_t:
            return self.__hdl_converter__.get_NameSlave2Master(self)
        
        if Inout == InOut_t.output_t:
            return self.__hdl_converter__.get_NameMaster2Slave(self)
        
        if varSigType== varSig.signal_t:
            return self.__hdl_converter__.get_NameSignal(self) 
            
        return self._type 

    def getTypes(self):
        return {
            "main" : self._type,
            "m2s"  : self.__hdl_converter__.get_NameMaster2Slave(self),
            "s2m"  : self.__hdl_converter__.get_NameSlave2Master(self)

        }        
        


    def flipInout(self):
        self._Inout = InoutFlip(self._Inout)
        members = self.getMember()
        for x in members:
            x["symbol"].flipInout()

    def resetInout(self):
        if self._Inout == InOut_t.Slave_t:
            self.flipInout()
        elif self._Inout == InOut_t.input_t:
            self.flipInout()
            
        self._Inout = InOut_t.Internal_t


    def setInout(self,Inout):
        if self._Inout == Inout:
            return 
        
        if self.__v_classType__ == v_classType_t.transition_t :
            self._Inout = Inout
        elif self.__v_classType__ == v_classType_t.Record_t  and Inout == InOut_t.Master_t:
            self._Inout = InOut_t.output_t
        elif self.__v_classType__ == v_classType_t.Record_t and Inout == InOut_t.Slave_t:
            self._Inout = InOut_t.input_t
        elif self.__v_classType__ == v_classType_t.Record_t:
            self._Inout = Inout
        
        elif self.__v_classType__ == v_classType_t.Master_t and Inout == InOut_t.Master_t:
            self._Inout = Inout
        elif self.__v_classType__ == v_classType_t.Slave_t and Inout == InOut_t.Slave_t:
            self._Inout = Inout    
        else:
            raise Exception("wrong combination of Class type and Inout type",self.__v_classType__,Inout)

        if Inout == InOut_t.Internal_t:
            Inout = InOut_t.Master_t 
        members = self.getMember()
        for x in members:
            x["symbol"].setInout(Inout)


    def set_varSigConst(self, varSigConst):
        self._varSigConst = varSigConst
        for x  in self.getMember():
            x["symbol"].set_varSigConst(varSigConst)
             

    def isInOutType(self, Inout):
        
        if Inout is None or self._Inout == Inout: 
            return True
        
        if self._Inout== InOut_t.Master_t:
            mem = self.getMember(Inout)
            return len(mem) > 0
        
        if self._Inout == InOut_t.Slave_t:
            if Inout == InOut_t.Master_t:
                Inout = InOut_t.Slave_t
            elif Inout == InOut_t.Slave_t:
                Inout = InOut_t.Master_t
            elif Inout == InOut_t.input_t:
                Inout = InOut_t.output_t
            elif Inout == InOut_t.output_t:
                Inout = InOut_t.input_t
            
            mem = self.getMember(Inout)
            return len(mem) > 0
            

    def isVarSigType(self, varSigType):
        if varSigType is None:
            return True

        return self._varSigConst == varSigType

        



    def get_master(self):
        raise Exception("Function not implemented")

    def get_slave(self):
        raise Exception("Function not implemented")


    def make_serializer(self):
        pass 

    
    def getMember(self,InOut_Filter=None, VaribleSignalFilter = None,name=None):
        ret = list()
        for x in self.__dict__.items():
            t = getattr(self, x[0])
            if not issubclass(type(t),argg_hdl_base) :
                continue 
            if not t.isInOutType(InOut_Filter):
                continue
            if x[0] == '__Driver__':
                continue
            if not t.isVarSigType(VaribleSignalFilter):
                continue
            if name and name == x[0]:
                return t

            ret.append({
                        "name": x[0],
                        "symbol": t
                    })

        ret =sorted(ret, key=lambda element_: element_["name"])
        return ret

    def _sim_get_new_storage(self):
        mem = self.getMember()
        for x in mem:
            x["symbol"]._sim_get_new_storage()

    def set_simulation_param(self,module, name,writer):
        members = self.getMember() 
        for x in members:
            x["symbol"].set_simulation_param(module+"."+name, x["name"], writer)
  
    def __str__(self):
        if self.__Driver__ and str( self.__Driver__) != 'process' and not isinstance(self.__Driver__,str):
            return str(self.__Driver__)

        if self.__hdl_name__:
            return str(self.__hdl_name__)

        raise Exception("Unable convert to string class: ", type(self).__name__)


    def _set_to_sub_connection(self):
        self.__Driver_Is_SubConnection__ = True
        for x in self.getMember():
            x["symbol"]._set_to_sub_connection()


    def _conect_members(self,rhs):
        self_members  = self.get_s2m_signals()
        rhs_members  = rhs.get_s2m_signals()

        for i,x in enumerate(self_members):
            rhs_members[i]['symbol'] << self_members[i]['symbol']
            rhs_members[i]['symbol']._set_to_sub_connection()

        self_members  = self.get_m2s_signals()
        rhs_members  = rhs.get_m2s_signals()
        for i,x in enumerate(self_members):
            self_members[i]['symbol'] << rhs_members[i]['symbol']
            self_members[i]['symbol']._set_to_sub_connection()


    def _connect(self,rhs):
        if self._Inout != rhs._Inout and self._Inout != InOut_t.Internal_t and rhs._Inout != InOut_t.Internal_t and rhs._Inout != InOut_t.Slave_t and self._Inout != InOut_t.Master_t and self._Inout != InOut_t.input_t and self._Inout != InOut_t.output_t:
            raise Exception("Unable to connect different InOut types")
        
        if type(self).__name__ != type(rhs).__name__:
            raise Exception("Unable to connect different types")

        self.__Driver__ = rhs
        rhs.__receiver__.append(self)
#       if not isConverting2VHDL():
        self._conect_members(rhs)
            


    def _connect_running(self,rhs):
        if self._Inout != rhs._Inout and self._Inout != InOut_t.Internal_t and rhs._Inout != InOut_t.Internal_t and rhs._Inout != InOut_t.Slave_t and self._Inout != InOut_t.Master_t and self._Inout != InOut_t.input_t and self._Inout != InOut_t.output_t:
            raise Exception("Unable to connect different InOut types")
        
        rhs = value(rhs)

        if type(self).__name__ != type(rhs).__name__:
            raise Exception("Unable to connect different types")
        
        
        self._conect_members(rhs)

    def __lshift__(self, rhs):
        if gsimulation.isRunning():
            self._connect_running(rhs)
        else:
            if self.__Driver__ and not isConverting2VHDL():
                raise Exception("symbol has already a driver", self.get_vhdl_name())
            self._connect(rhs)


    def _get_Stream_input(self):
        return  self

    def _get_Stream_output(self):
        return self
    
    def __or__(self,rhs):
        
        rhs_StreamIn = rhs._get_Stream_input()
        self_StreamOut = self._get_Stream_output()
        
        ret = v_entity_list()


        ret.append(self)
        ret.append(rhs)

        rhs_StreamIn << self_StreamOut
        return ret
        
    def _issubclass_(self,test):
        if super()._issubclass_(test):
            return True
        return "v_class" == test
    
    def _instantiate_(self):
        if self.__isInst__:
            return
        
        
        self_members = self.getMember()
        for x in self_members:
            x["symbol"]._instantiate_()
        


        self._Inout = InoutFlip(self._Inout)
        self.__isInst__ = True
        return self
    
    def _un_instantiate_(self, Name = ""):
        if not self.__isInst__:
            return
        self_members = self.getMember()
        for x in self_members:
            x["symbol"]._un_instantiate_(x["name"])
        
        
        self.setInout(InoutFlip(self._Inout))
        self.set_vhdl_name(Name,True)
        #self._Inout = InoutFlip(self._Inout)
        self.__isInst__ = False
        return self

    def get_m2s_signals(self):
        linput = InOut_t.input_t
        louput = InOut_t.output_t




        if self.__v_classType__ ==v_classType_t.Record_t :
            self_members = self.getMember()
            return self_members
                
        if  self._Inout == InOut_t.Master_t:
            self_members = self.getMember(louput)
            return self_members
            
        if  self._Inout == InOut_t.Slave_t:
            self_members = self.getMember(linput)
            return self_members
        
        if  self._Inout == InOut_t.Internal_t:
            self_members = self.getMember(louput)
            return self_members            
        
    def get_s2m_signals(self):
        linput = InOut_t.input_t
        louput = InOut_t.output_t



        if self.__v_classType__ ==v_classType_t.Record_t:
            return []
        
        if  self._Inout == InOut_t.Master_t:
            self_members = self.getMember(linput)
            return self_members
            
        if  self._Inout == InOut_t.Slave_t:
            self_members = self.getMember(louput)
            return self_members
        
        if  self._Inout == InOut_t.Internal_t:
            self_members = self.getMember(linput)
            return self_members      
            
 

    def _remove_drivers(self):
        self.__Driver__ = None
        mem = self.getMember()
        for x in mem:
            x["symbol"]._remove_drivers()

add_constructor("v_class",v_class)