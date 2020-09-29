from argg_hdl.argg_hdl_base import *
from argg_hdl.argg_hdl_v_function import *
from argg_hdl.argg_hdl_v_entity_list import *

import  argg_hdl.converter.vhdl_v_class_helpers as  vc_helper
from argg_hdl.argg_hdl_lib_enums import  varSig, InOut_t, v_classType_t
import argg_hdl.argg_hdl_v_Package as argg_pack
from argg_hdl.converter.argg_hdl_v_class_converter import v_class_converter
from argg_hdl.argg_hdl_v_class import   v_class
from argg_hdl.argg_hdl__primitive_type_converter  import add_primitive_hdl_converter
import  argg_hdl.argg_hdl_hdl_converter as  hdl

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
    
    def getMemeber_Connect(self,obj, InOut_Filter,PushPull,PushPullPrefix=""):
        ret = []
        

            
        members = obj.getMember() 
        
        for x in members:
            if x["symbol"]._Inout == InOut_t.Internal_t:
                continue
            ys =hdl.extract_conversion_types(
                x["symbol"],
                exclude_class_type= v_classType_t.transition_t,
                filter_inout=InOut_Filter)
            for y in ys:
                suffix = "_01(clk, self." if is_variable(y) else "_11(clk, self_sig."
                ret.append(PushPull+suffix+ x["name"]+", "+PushPullPrefix + x["name"] +");")
        return ret     

    def extract_conversion_types_Master_Slave_impl(self, obj, exclude_class_type=None,filter_inout=None,VarSig=None,Suffix=""):
        ret = []
        if VarSig == varSig.signal_t:
            name = obj.__hdl_converter__.get_NameSignal(obj)
        else:
            name = obj._type
        x = v_class(name, VarSig)
        x.__v_classType__ = v_classType_t.Record_t
        x.__abstract_type_info__.vetoHDLConversion = True
        
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
        argumentList = "signal clk : in std_logic; "
        argumentList += obj.__hdl_converter__.getMemberArgs(
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
        )

        ret  = v_procedure(
            name=procedureName, 
            argumentList=argumentList , 
            body=body,
            IsEmpty=len(body.strip()) == 0,
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
            x 
            for x in ret
            if not( x["symbol"]._issubclass_("v_class")  and exclude_class_type and x["symbol"].__v_classType__ == exclude_class_type)
            if not(filter_inout and x["symbol"]._Inout != filter_inout)
        ]
         

        return ret1
    
    def get_process_sensitivity_list(self, obj):
        content = []
        for x in obj.getMember( ):
            n_connector = vc_helper._get_connector( x["symbol"])
            if n_connector is None:
                continue

            inout = InOut_t.input_t if x["symbol"]._Inout == InOut_t.Master_t else InOut_t.output_t

            ys =n_connector.__hdl_converter__.extract_conversion_types(
                    n_connector,
                    exclude_class_type= v_classType_t.transition_t,
                    filter_inout=InOut_t.input_t
                )
            for y in ys:
                content.append( y["symbol"].get_vhdl_name() )

        ys = hdl.extract_conversion_types(obj)
        content += [ x["symbol"] for x in ys if x["symbol"]._varSigConst == varSig.signal_t ]
        return content




    def make_function_variable_assignment(self, obj,func_arg, arg):
        ret = []
        ys =func_arg["symbol"].__hdl_converter__.extract_conversion_types(func_arg["symbol"])
        for y in ys:
            line = func_arg["name"] + y["suffix"]+ " => " + str(arg) + y["suffix"]
            ret.append(line)

        return ret

    def to_arglist(self,obj, name,parent, withDefault = False, astParser=None):
        ret = []
        
        xs = hdl.extract_conversion_types(obj)

        for x in xs:
            inoutstr =  " inout " # fixme 

            varSignal = "" if x["symbol"]._varSigConst == varSig.variable_t else " Signal "
            Default_str =  " := " + hdl.get_default_value(obj) \
                if withDefault and obj.__writeRead__ != InOut_t.output_t and obj._Inout != InOut_t.output_t \
                else ""

            TypeName = hdl.get_type_simple(x["symbol"])
            ret.append(varSignal + name + x["suffix"] + " : " + inoutstr +" " +  TypeName +Default_str)
            

        r =join_str(ret,Delimeter="; ",IgnoreIfEmpty=True)
        return r


add_primitive_hdl_converter("v_class_hanlde",v_class_hanlde_converter )