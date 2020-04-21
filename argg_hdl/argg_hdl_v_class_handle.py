from argg_hdl.argg_hdl_base import *
from argg_hdl.argg_hdl_v_function import *
from argg_hdl.argg_hdl_v_entity_list import *

import  argg_hdl.vhdl_v_class_helpers as  vc_helper
import argg_hdl.argg_hdl_v_Package as argg_pack

from argg_hdl.argg_hdl_v_class import v_class_converter,  v_class

class v_class_hanlde_converter(v_class_converter):
    def __init__(self):
        super().__init__()

    def make_connection(self, obj, name, parent):
          
        obj.pull       =  obj.__hdl_converter__.getConnecting_procedure(obj, InOut_t.input_t , "pull")
        obj.push       =  obj.__hdl_converter__.getConnecting_procedure(obj, InOut_t.output_t, "push")

        if obj.__vectorPull__:
            obj.vpull       =  obj.__hdl_converter__.getConnecting_procedure_vector(obj, InOut_t.input_t , "pull",procedureName="pull")
        if obj.__vectorPush__:
            obj.vpush       =  obj.__hdl_converter__.getConnecting_procedure_vector(obj, InOut_t.output_t, "push",procedureName="push")

    def getConnecting_procedure_vector(self,obj, InOut_Filter,PushPull,procedureName=None):
        procedure_maker =  vc_helper.getConnecting_procedure_vector(obj, InOut_Filter,PushPull,procedureName)

        return procedure_maker.get_procedure()
    
    def extract_conversion_types_Master_Slave_impl(self, obj, exclude_class_type=None,filter_inout=None,VarSig=None,Suffix=""):
        ret = []
        if VarSig == varSig.signal_t:
            name = obj.__hdl_converter__.get_NameSignal(obj)
        else:
            name = obj._type
        x = v_class(name, VarSig)
        x.__v_classType__ = v_classType_t.Record_t
        x.__vetoHDLConversion__  = True
        x._Inout= obj._Inout
        x.__writeRead__ = obj.__writeRead__
        x.__hdl_name__ = vc_helper.append_hdl_name(str(obj.__hdl_name__),Suffix)
        ys= obj.getMember(VaribleSignalFilter=VarSig)
        if len(ys)>0:
            for y in ys: 
                setattr(x, y["name"], y["symbol"])
            
            ret.append({ "suffix":Suffix, "symbol": x})
        return ret


    def getMember_InternalConnections(self,obj, InOut_Filter,PushPull):
        ret = []

        members = obj.__hdl_converter__.get_internal_connections(obj)
        for x in members:
            inout_local = vc_helper.InoutFlip_if(InOut_Filter, x["type"] == 'sig2var')
            connector   = vc_helper.if_true_get_first(PushPull == "pull", [".","_"])
            
            sig =x["destination"]["symbol"].__hdl_converter__.extract_conversion_types(
                x["destination"]["symbol"],
                exclude_class_type= v_classType_t.transition_t,
                filter_inout=inout_local
            )
            
            ret.append(PushPull + "(" +obj.__hdl_name__+"."+x["destination"]["name"] +", "  +obj.__hdl_name__+"_sig" + connector + x["source"]["name"]+ sig[0]["suffix"] +")" )
        return ret
        
    def getConnecting_procedure(self,obj, InOut_Filter,PushPull, procedureName=None):
        ClassName=None

        beforeConnecting, AfterConnecting, inout = obj.__hdl_converter__.get_before_after_conection(
            obj,
            InOut_Filter, 
            PushPull
        )
        
        argumentList = obj.__hdl_converter__.getMemberArgs(
            obj, 
            InOut_Filter,
            inout,
            IncludeSelf = True,
            PushPull=PushPull
        )
        
        Connecting = obj.__hdl_converter__.getMemeber_Connect(
            obj, 
            InOut_Filter,
            PushPull
        )

        internal_connections = obj.__hdl_converter__.getMember_InternalConnections(
            obj, 
            InOut_Filter,
            PushPull
        )

        Connecting = join_str(
            [Connecting, internal_connections],
            LineEnding="\n",
            LineBeginning="    " ,
            IgnoreIfEmpty = True 
        )

        IsEmpty=  \
            len(Connecting.strip()) == 0 \
                and \
            len(beforeConnecting.strip()) == 0 \
                and  \
            len(AfterConnecting.strip()) == 0

        ret  = v_procedure(
            name=procedureName, 
            argumentList=argumentList , 
            body='''
    {beforeConnecting}
-- Start Connecting
{Connecting}
-- End Connecting
    {AfterConnecting}
            '''.format(
               beforeConnecting=beforeConnecting,
               Connecting = Connecting,
               AfterConnecting=AfterConnecting
            ),
            IsEmpty=IsEmpty,
            isFreeFunction=True
            )
        
        return ret




    def extract_conversion_types_Master_Slave(self, obj, exclude_class_type=None,filter_inout=None):
        ret = []
        ret += obj.__hdl_converter__.extract_conversion_types_Master_Slave_impl(
            obj,
            exclude_class_type,
            filter_inout,
            varSig.signal_t,
            "_sig"
        )
        ret += obj.__hdl_converter__.extract_conversion_types_Master_Slave_impl(
            obj, 
            exclude_class_type,
            filter_inout,
            varSig.variable_t,
            ""
        )

        return ret

    def extract_conversion_types(self, obj, exclude_class_type=None,filter_inout=None):
        ret =[]

       
        ret = obj.__hdl_converter__.extract_conversion_types_Master_Slave(
                obj, 
                exclude_class_type,
                filter_inout
        )

        

        ret1 = [
            x for x in ret
            if not( x["symbol"]._issubclass_("v_class")  and exclude_class_type and x["symbol"].__v_classType__ == exclude_class_type)
            if not(filter_inout and x["symbol"]._Inout != filter_inout)
        ]
         

        return ret1

class v_class_hanlde(v_class):
    def __init__(self,Name=None,varSigConst=None):
        super().__init__(Name,varSigConst)
        self.__hdl_converter__ = v_class_hanlde_converter()
        self.__vectorPush__   = True
        self.__vectorPull__   = True
        self._varSigConst       = varSig.combined_t


    def getType(self,Inout=None,varSigType=None):
        if self.__v_classType__ == v_classType_t.Record_t:
             return self._type 
        
        if Inout == InOut_t.input_t:
            return self.__hdl_converter__.get_NameSlave2Master(self)
        
        if Inout == InOut_t.output_t:
            return self.__hdl_converter__.get_NameMaster2Slave(self)
        
        if varSigType== varSig.signal_t:
            return self.__hdl_converter__.get_NameSignal(self) 
            
        return self._type 



