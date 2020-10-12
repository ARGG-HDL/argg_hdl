from argg_hdl.argg_hdl_base import *
from argg_hdl.argg_hdl_v_function import *
from argg_hdl.argg_hdl_v_entity_list import *
from argg_hdl.argg_hdl_simulation import *
import argg_hdl.argg_hdl_v_Package as argg_pack
import  argg_hdl.converter.vhdl_v_class_helpers as  vc_helper
from argg_hdl.argg_hdl_v_class import  v_class
from argg_hdl.converter.argg_hdl_v_class_converter import v_class_converter
from argg_hdl.argg_hdl_lib_enums import  varSig, InOut_t, v_classType_t
from argg_hdl.argg_hdl__primitive_type_converter  import add_primitive_hdl_converter
import  argg_hdl.argg_hdl_hdl_converter as  hdl

class v_class_trans_converter(v_class_converter):
    def __init__(self):
        super().__init__()

    def _vhdl__reasign(self, obj, rhs, astParser=None,context_str=None):
        
        asOp = obj.__hdl_converter__.get_assiment_op(obj)

        
        if rhs._Inout == InOut_t.Master_t:
            raise Exception("cannot read from Master")
        if rhs._Inout == InOut_t.output_t:
            raise Exception("cannot read from Output")


        
        if rhs._type != obj._type:
            raise Exception("cannot assigne different types.", str(obj), rhs._type, obj._type )
        
        ret ="---------------------------------------------------------------------\n--  " + \
                obj.get_vhdl_name() +" << " + rhs.get_vhdl_name()+"\n" 
        ret += obj.get_vhdl_name(InOut_t.output_t) + asOp + rhs.get_vhdl_name(InOut_t.output_t) +";\n" 
        ret += rhs.get_vhdl_name(InOut_t.input_t) + asOp + obj.get_vhdl_name(InOut_t.input_t)
        return ret 



    def impl_get_attribute(self,obj, attName,parent=None):
        attName = str(attName)

        if is_handle_class(parent):
            return obj.get_vhdl_name() + "." +str(attName)
        
        
        xs = obj.__hdl_converter__.extract_conversion_types(obj)
           
        for x in xs:
            for y in x["symbol"].getMember():
                if y["name"] == attName:
                    return obj.get_vhdl_name() + x["suffix"] + "." +   attName


           
        return obj.get_vhdl_name() + "." +str(attName)


    def make_connection(self, obj, name, parent):
        obj.pull          =  obj.__hdl_converter__.getConnecting_procedure(obj, InOut_t.input_t , "pull_01", procedureName="pull_01",varSig_=varSig.variable_t)
        obj.push          =  obj.__hdl_converter__.getConnecting_procedure(obj, InOut_t.output_t, "push_01", procedureName="push_01",varSig_=varSig.variable_t)
        obj.pull_rev      =  obj.__hdl_converter__.getConnecting_procedure(obj, InOut_t.output_t, "pull_01", procedureName="pull_01",varSig_=varSig.variable_t)
        obj.push_rev      =  obj.__hdl_converter__.getConnecting_procedure(obj, InOut_t.input_t , "push_01", procedureName="push_01",varSig_=varSig.variable_t)

        obj.pull_sig      =  obj.__hdl_converter__.getConnecting_procedure(obj, InOut_t.input_t , "pull_11", procedureName="pull_11",varSig_=varSig.signal_t)
        obj.push_sig      =  obj.__hdl_converter__.getConnecting_procedure(obj, InOut_t.output_t, "push_11", procedureName="push_11",varSig_=varSig.signal_t)
        obj.pull_rev_sig  =  obj.__hdl_converter__.getConnecting_procedure(obj, InOut_t.output_t, "pull_11", procedureName="pull_11",varSig_=varSig.signal_t)
        obj.push_rev_sig  =  obj.__hdl_converter__.getConnecting_procedure(obj, InOut_t.input_t , "push_11", procedureName="push_11",varSig_=varSig.signal_t)
            
    def getConnecting_procedure(self,obj, InOut_Filter,PushPull, procedureName=None,varSig_=varSig.variable_t):
        
        beforeConnecting, AfterConnecting, inout = obj.__hdl_converter__.get_before_after_conection(
            obj,
            InOut_Filter, 
            PushPull
        )


        classType = obj.getType(InOut_Filter)
        ClassName="IO_data"
        varSig__str = "" if varSig_ == varSig.variable_t else " signal "
        type_name  = self.get_type_simple(obj)
        
        argumentList = "signal clk : in std_logic; "
        argumentList += varSig__str + " self : inout " + type_name
        argumentList += " ; signal " + ClassName +" : " + inout+ classType


        Connecting = obj.__hdl_converter__.getMemeber_Connect(
            obj, 
            InOut_Filter,
            PushPull, 
            ClassName+"."
        )

        Connecting = join_str(
            [Connecting],
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

        ret        = v_procedure(
            name=procedureName, 
            argumentList=argumentList , 
            body=body,
            IsEmpty=len(body.strip()) == 0,
            isFreeFunction=True
            )
        
        return ret     

        
    def impl_symbol_instantiation(self, obj ,VarSymb=None):
        print_cnvt("impl_symbol_instantiation is deprecated")
        if not VarSymb:
            VarSymb = get_varSig(obj._varSigConst)

        if obj.__Driver__ and str( obj.__Driver__) != 'process':
            return ""
        t = obj.getTypes()
        ret = ""
        ret += VarSymb + " " +str(obj) + "_m2s : " + t["m2s"] +" := " + t["m2s"]+"_null;\n"
        ret += VarSymb + " " +str(obj) + "_s2m : " + t["s2m"] +" := " + t["s2m"]+"_null;\n"
        return ret

    def extract_conversion_types_transition_type_impl(self, obj, exclude_class_type=None,filter_inout=None,Inout=None):
        ret =[]
        if Inout == InOut_t.input_t:
            name = obj.__hdl_converter__.get_NameSlave2Master(obj)
            suffix="_s2m"

        else:
            name = obj.__hdl_converter__.get_NameMaster2Slave(obj)
            suffix = "_m2s"



        x = v_class(name, obj._varSigConst)
        x.__v_classType__ = v_classType_t.Record_t
        x.__abstract_type_info__.vetoHDLConversion = True
        
        x.__hdl_name__ =vc_helper.append_hdl_name(obj.__hdl_name__,suffix)
        x._Inout=Inout
        if obj._Inout == InOut_t.input_t or obj._Inout == InOut_t.Slave_t:
            x._Inout=InoutFlip(x._Inout)
            Inout =InoutFlip(Inout)
           
        ys= obj.getMember(Inout)
        for y in ys: 
            setattr(x, y["name"], y["symbol"])
        ret.append({ "suffix":suffix, "symbol": x})

        return ret

    def extract_conversion_types_transition_type(self, obj, exclude_class_type=None,filter_inout=None):
        ret =[]
        ret += obj.__hdl_converter__.extract_conversion_types_transition_type_impl(
            obj, 
            exclude_class_type,
            filter_inout,
            InOut_t.input_t
        )
        ret += obj.__hdl_converter__.extract_conversion_types_transition_type_impl(
            obj, 
            exclude_class_type,
            filter_inout,
            InOut_t.output_t
        )
        
        ret.append({ "suffix":"", "symbol": obj})
        return ret

    def extract_conversion_types(self, obj, exclude_class_type=None,filter_inout=None):

                
        ret = obj.__hdl_converter__.extract_conversion_types_transition_type(
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


add_primitive_hdl_converter("v_class_trans",v_class_trans_converter )
