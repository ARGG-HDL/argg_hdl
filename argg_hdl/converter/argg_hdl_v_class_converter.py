import os
import sys
import inspect


from argg_hdl.argg_hdl_base import *
from argg_hdl.argg_hdl_v_function import *
from argg_hdl.argg_hdl_v_entity_list import *
from argg_hdl.argg_hdl_simulation import *
from argg_hdl.argg_hdl_v_class import *
import argg_hdl.argg_hdl_v_Package as argg_pack
import  argg_hdl.converter.vhdl_v_class_helpers as  vc_helper

import  argg_hdl.argg_hdl_hdl_converter as  hdl

from  argg_hdl.argg_hdl_object_name_maker import  make_object_name
from argg_hdl.argg_hdl_object_factory import add_constructor

from argg_hdl.argg_hdl__primitive_type_converter  import add_primitive_hdl_converter



def flat_member_list(obj, name):
    ret = []
    
    if obj._issubclass_('v_symbol'):
        return [{
            "name": name,
            "symbol" :obj
            }]
    
    for m in obj.getMember():
        ret += flat_member_list(m["symbol"],name + [m["name"]] )
    
    return ret


    

class v_class_converter(hdl_converter_base):
    def __init__(self):
        super().__init__()
        self.__ast_functions__ =list()
        self.archetecture_list = []
        self.functionNameVetoList= []
        self.extractedTypes = []
        self.Constructor_Default_arguments=[]

    def def_includes(self,obj, name,parent):
        ret = ""
        for x in obj.__dict__.items():
            t = getattr(obj, x[0])
            if issubclass(type(t),argg_hdl_base):
                        
                ret += hdl.def_includes(t,x[0],obj)
        
        for x in obj.__hdl_converter__.__ast_functions__:
            ret += hdl.def_includes(x,None,obj)

        ret += "use work."+ hdl.get_type_simple(obj)+"_pack.all;"
        return ret

    def get_packet_file_name(self, obj):

        return hdl.get_type_simple(obj)+"_pack.vhd"

    def get_packet_file_content(self, obj):
        PackageName = hdl.get_type_simple(obj)+"_pack"
        s = isConverting2VHDL()
        set_isConverting2VHDL(True)


        pack  = argg_pack.v_package(PackageName,sourceFile=obj.__srcFilePath__,
            PackageContent = [
                obj
            ])

        fileContent = pack.to_string()
        set_isConverting2VHDL(s)
        return fileContent




    def def_record_Member(self,obj, name,parent,Inout=None):
        if not issubclass(type(parent),v_class):
            return []

        if obj._Inout == InOut_t.Slave_t:
            Inout = InoutFlip(Inout)

        if not(obj._varSigConst == varSig.signal_t and Inout == InOut_t.InOut_tt):
            return name + " : " +obj.getType(Inout)
        
        ret = []
        xs = hdl.extract_conversion_types(
            obj,
            exclude_class_type=v_classType_t.transition_t
        )
        for x in xs:
            ret.append(name + x["suffix"] + " : " + x["symbol"].getType())
        return ret
            
        
        

    def def_record_Member_Default(self, obj, name,parent,Inout=None):
        

        
        if obj._Inout == InOut_t.Slave_t:
            Inout = InoutFlip(Inout)
        
        if not( obj._varSigConst == varSig.signal_t and Inout == InOut_t.InOut_tt):
            return name + " => " + hdl.impl_get_init_values(obj, parent=parent, InOut_Filter=Inout)
        
        ret = []
        xs = hdl.extract_conversion_types(
            obj,
            exclude_class_type=v_classType_t.transition_t
        )
        for x in xs:
            ret.append(name + x["suffix"] + " => " + hdl.impl_constructor(x["symbol"])  )
        return ret
            

    def get_constroctor_default_list(self,obj):
        primary = hdl.get_primary_object(obj)
        if primary.__hdl_converter__.Constructor_Default_arguments:
            return primary.__hdl_converter__.Constructor_Default_arguments
        
        
        fl = flat_member_list(primary, [])
        primary.__hdl_converter__.Constructor_Default_arguments =[
            x
            for x in fl
            if not x["symbol"].__abstract_type_info__.UseDefaultCtr
        ]
        return primary.__hdl_converter__.Constructor_Default_arguments


    def impl_get_init_values(self,obj, parent=None, InOut_Filter=None, VaribleSignalFilter = None,ForceExpand=False):
        primary = hdl.get_primary_object(obj)
        
        if ForceExpand:
            member = obj.getMember()
            Content = [
                hdl.def_record_Member_Default(
                x["symbol"], 
                x["name"],
                obj.getMember(name=x["name"]),
                InOut_Filter
                ) 
                for x in member
            ]
            start = "(\n"
            ret=join_str(
                Content,
                start= start ,
                end=  "\n  )",
                Delimeter=",\n",
                LineBeginning= "    ", 
                IgnoreIfEmpty=True
            )
            return ret

        TypeName = hdl.get_type_simple(parent)
        name = TypeName +"_ctr"
        Constructor_Default_arguments=self.get_constroctor_default_list(obj)
        fl = flat_member_list(obj, [])
       # print(name, Constructor_Default_arguments, fl)
        
        argList = [join_str(x["name"],Delimeter="_") + "  =>  "  + str(value(x["symbol"]))
            for i, x in enumerate(fl)
            if not x["symbol"].__abstract_type_info__.UseDefaultCtr
            if len(Constructor_Default_arguments)> i and value(x["symbol"]) !=  value(Constructor_Default_arguments[i]["symbol"])
            ]
        Argliststr = join_str(argList,Delimeter=", ",IgnoreIfEmpty=True ,start = "(" ,end = ")" )

        ret  = name +Argliststr
        return ret
        

    def make_constructor(self,obj,name,parent=None,InOut_Filter=None, VaribleSignalFilter = None ):
        primary = hdl.get_primary_object(obj)

        TypeName = hdl.get_type_simple(primary)
        member = primary.getMember()  

        VariableList = "  variable ret : "  + TypeName+ " := " + TypeName +"_null;"

        name = TypeName +"_ctr"
        
        fl = flat_member_list(primary, [])
        

        Constructor_Default_arguments=self.get_constroctor_default_list(obj)
        argList = [
            join_str(x["name"],Delimeter="_") + " : integer := " + str(value(x["symbol"]))
            for x in Constructor_Default_arguments 
            ]
        Argliststr = join_str(argList,Delimeter="; ",IgnoreIfEmpty=True)

        body= [
            "    ret." + join_str(x["name"],Delimeter=".")  + " := "+  hdl.get_type_simple(x["symbol"]) + "_ctr(" + join_str(x["name"],Delimeter="_")   +");\n"
            for x in Constructor_Default_arguments 
        ]
        body = join_str(body,IgnoreIfEmpty=True)
        body += "    return ret;\n"

        func = v_function(body=body, returnType=TypeName, argumentList=Argliststr,VariableList=VariableList,name=name,IsEmpty=False,isFreeFunction=True)
        setattr(parent, name, func)

        


    def def_def_make_constant(self, obj, name,parent=None,InOut_Filter=None, VaribleSignalFilter = None):
        TypeName = hdl.get_type_simple(obj)
        member = obj.getMember()

        defaults  = hdl.impl_get_init_values(
            obj=obj,
            parent=parent, 
            InOut_Filter=InOut_Filter, 
            VaribleSignalFilter=VaribleSignalFilter,
            ForceExpand=True
        )   
        if not defaults.strip():
            return ""

        ret = "\n  constant " + name + " : " + TypeName + ":= " + defaults +';\n'

        return ret

    def prepare_for_conversion(self,obj):
        primary = hdl.get_primary_object(obj)
        obj.__hdl_converter__ = primary.__hdl_converter__
        if not primary.__hdl_converter__.extractedTypes:
            primary.__hdl_converter__.extractedTypes += vc_helper.extract_components(primary)

        members = obj.getMember()
        for m in members:
            hdl.prepare_for_conversion(m["symbol"])


    def def_packet_header(self,obj, name,parent):
        if issubclass(type(parent),v_class):
            return ""

        header = vc_helper.getHeader(obj, name,parent)

        return str(header)
        
    

    def getHeader_make_record(self,obj, name, parent=None, InOut_Filter=None, VaribleSignalFilter = None):
        TypeName = hdl.get_type_simple(obj)
        member = obj.getMember()
        start= "\ntype "+TypeName+" is record \n"
        end=  """end record;
    
    {Default}

    type {TypeName}_a is array (natural range <>) of {TypeName};
        """.format(
          Default = obj.__hdl_converter__.def_def_make_constant(
                obj,
                TypeName + "_null" , 
                parent, 
                InOut_Filter,
                VaribleSignalFilter
              ),
          TypeName=TypeName  
        )

        
        Content = [
            hdl.def_record_Member(x["symbol"],x["name"],obj,InOut_Filter)
            for x in member
        ]
        ret=join_str(Content,start= start ,end= end, IgnoreIfEmpty=True,LineEnding=";\n", LineBeginning="    ")

        self.make_constructor( obj,
                TypeName + "_null" , 
                parent, 
                InOut_Filter,
                VaribleSignalFilter)

        return ret

    def make_connection(self, obj, name, parent):
        pass
        




        

    def getBody_onPush(self, obj):
        for x in obj.__hdl_converter__.__ast_functions__:
            if "_onpush" in x.name.lower()  and not "_onpush_comb" in x.name.lower():
                return x.body
        return ""

    def getBody_onPull(self, obj):
        for x in obj.__hdl_converter__.__ast_functions__:
            if  "_onpull" in x.name.lower() and not "_onpull_comb" in x.name.lower():
                return x.body
        return ""


    def getBody_onPush_comb(self, obj):
        for x in obj.__hdl_converter__.__ast_functions__:
            if "_onpush_comb" in x.name.lower():
                return x.body
        return ""

    def getBody_onPull_comb(self, obj):
        for x in obj.__hdl_converter__.__ast_functions__:
            if  "_onpull_comb" in x.name.lower() :
                return x.body
        return ""


    def get_before_after_conection(self, obj, InOut_Filter, PushPull):
        beforeConnecting = ""
        AfterConnecting = ""
        
        if  "push" in PushPull:
            inout = " out "
            beforeConnecting_comb = obj.__hdl_converter__.getBody_onPush_comb(obj)
            beforeConnecting = obj.__hdl_converter__.getBody_onPush(obj)
            if beforeConnecting.strip():
                beforeConnecting =  "  if rising_edge(clk) then\n" + beforeConnecting + "  end if;"

            if beforeConnecting_comb.strip():
                beforeConnecting +="\n"+beforeConnecting_comb

        else:
            inout = " in "
            AfterConnecting_comb = obj.__hdl_converter__.getBody_onPull_comb(obj)
            AfterConnecting = obj.__hdl_converter__.getBody_onPull(obj)
            if AfterConnecting.strip():
                AfterConnecting =  "  if rising_edge(clk) then\n" + AfterConnecting + "  end if;"
            if AfterConnecting_comb.strip():
                AfterConnecting = AfterConnecting_comb + "\n" +AfterConnecting
            
        return beforeConnecting, AfterConnecting, inout


    def def_packet_body(self,obj, name,parent):
        if issubclass(type(parent),v_class):
            return ""
        start  = "-------------------------------------------------------------------------\n"
        start += "------- Start Psuedo Class " +obj.getName() +" -------------------------\n"
        end  = "------- End Psuedo Class " +obj.getName() +" -------------------------\n  "
        end += "-------------------------------------------------------------------------\n\n\n"
  
        
        for x in obj.__dict__.items():
            t = getattr(obj, x[0])
            if issubclass(type(t),argg_hdl_base):
                start += hdl.def_packet_body(t,x[0],obj)

        content2 =  [
            hdl.def_packet_body(x,None,None) 
            for x in obj.__hdl_converter__.__ast_functions__ 
            if not ("_onpull" in x.name.lower()   or  "_onpush" in x.name.lower() )
        ]


        ret=join_str(content2, start=start,end=end)
        
        

        return ret
    
    def impl_symbol_instantiation(self, obj ,VarSymb=None):
        print_cnvt("impl_symbol_instantiation is deprecated")
        
        VarSymb =  VarSymb if VarSymb else  get_varSig(obj._varSigConst)

        if obj.__Driver__ and str( obj.__Driver__) != 'process':
            return ""

        
        TypeName = hdl.get_type_simple(obj)
        return VarSymb +" " +str(obj) + " : " + TypeName +" := " + hdl.impl_constructor(obj) +";\n"
    

    def impl_architecture_header(self, obj):
        ret = []

        for x in hdl.get_extractedTypes(obj):
            ret +=  x.impl_architecture_header(obj)
            
        
        for x in obj.__hdl_converter__.archetecture_list:
            ret.append( hdl.impl_architecture_header(x["symbol"]))




        ret=join_str(
            ret, 
            LineBeginning="  "
            )


        return ret
        
    def impl_architecture_body(self, obj):
        primary = hdl.get_primary_object(obj)
        obj.__hdl_converter__ = primary.__hdl_converter__
        ret = []
        for x in obj.__hdl_converter__.archetecture_list:
            ret.append(hdl.impl_architecture_body(x["symbol"]))
        
        ret=join_str(
            ret, 
            LineBeginning="  "
            )
        ret=ret.replace("!!SELF!!",str(obj.__hdl_name__))
        return ret


    def def_entity_port(self,obj):
        ret = []
        for x in hdl.get_extractedTypes(obj):
            ret += x.def_entity_port(obj)

        return ret


    def impl_entity_port(self, obj, name):
        ret = []
        for x in  hdl.get_extractedTypes(obj):
            ret += x.vhdl_make_port(obj,name)

        return ret


           
    def get_free_symbols(self,obj,name, parent_list=[]):
        
        member = obj.getMember()
        ret =[]
        for m in member:
            ret += hdl.get_free_symbols(m["symbol"], m["name"], parent_list +[{"symbol" :obj  , "name":name}])
       
        return ret


           
        
    def get_process_combinatorial_pull(self,obj, clk):
        ret = []
        Pull_Push_handle = vc_helper.vhdl__Pull_Push(obj,InOut_t.input_t, clk)
        st = str(Pull_Push_handle)
        if st:
            ret +=[st]
        return ret

    def get_process_combinatorial_push(self,obj,clk):
        ret = []
        Pull_Push_handle = vc_helper.vhdl__Pull_Push(obj,InOut_t.output_t,clk)
        st = str(Pull_Push_handle)
        if st:
            ret +=[st]
        return ret


    def Has_pushpull_function(self,obj, pushpull):
        
        pushpull = pushpull.lower()
        a= obj.__dir__()
        a= [x.lower()  for x in a]
        if pushpull == "pull":
            if "_onpull" in a:
                return True
            
            mem = obj.getMember(InOut_t.input_t)
            if len(mem) >0:
                return True

        if pushpull == "push":
            if "_onpush" in a:
                return True
            
            mem = obj.getMember(InOut_t.output_t)
            if len(mem) >0:
                return True   

        return False

 




    def getMemberArgs(self,obj, InOut_Filter,InOut,suffix="", IncludeSelf =False,PushPull=""):
        args = vc_helper.getMemberArgs(obj, InOut_Filter,InOut,suffix, IncludeSelf, PushPull)
        return str(args)
        
    def get_internal_connections(self,obj):
        ret = []
        members = obj.getMember() 
        for dest in members:
            d = dest["symbol"].__Driver__
            source = [x for x in members if x["symbol"] is d]
            if not source:
                continue

            c_type = "Unset"
            if dest["symbol"]._varSigConst == varSig.signal_t and source[0]["symbol"]._varSigConst == varSig.variable_t:
                c_type = "var2sig"
            elif dest["symbol"]._varSigConst ==  varSig.variable_t and source[0]["symbol"]._varSigConst == varSig.signal_t:
                c_type = "sig2var"
            ret.append({
                "source" : source[0],
                "destination" : dest,
                "type" : c_type
            })
        
        return ret 




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

                ret.append(PushPull+"(clk, self." + x["name"]+", "+PushPullPrefix + x["name"] +");")
        return ret      
         
 
    def impl_reasign(self, obj, rhs, astParser=None,context_str=None):
        
        asOp = hdl.get_assiment_op(obj)

        
        if rhs._Inout == InOut_t.Master_t and rhs._varSigConst == varSig.signal_t:
            raise Exception("cannot read from Master")
        if rhs._Inout == InOut_t.output_t and rhs._varSigConst == varSig.signal_t:
            raise Exception("cannot read from Output")


        obj._add_output()
        
        if obj.__v_classType__ == v_classType_t.Master_t or obj.__v_classType__ == v_classType_t.Slave_t:
            hdl_call = hdl.impl_function_call(obj, "__lshift__",[obj, rhs],astParser)
            if hdl_call is None:
                astParser.Missing_template=True
                return "-- $$ template missing $$"
            return hdl_call


            
        if rhs._type != obj._type:
            raise Exception("cannot assigne different types.", str(obj), rhs._type, obj._type )
        return obj.get_vhdl_name() + asOp +  rhs.get_vhdl_name()
    
    def impl_reasign_rshift_(self, obj, rhs, astParser=None,context_str=None):
        if obj.__v_classType__ == v_classType_t.Master_t or obj.__v_classType__ == v_classType_t.Slave_t:
            hdl_call = hdl.impl_function_call(obj, "__rshift__",[obj, rhs],astParser)
            if hdl_call is None:
                astParser.Missing_template=True
                return "-- $$ template missing $$"
            return hdl_call
        raise Exception("Unsupported r shift", str(obj), rhs._type, obj._type )

    def get_self_func_name(self, obj, IsFunction = False, suffix = ""):
        xs = hdl.extract_conversion_types(obj ,filter_inout=InOut_t.Internal_t)
        content = []
             

        for x in xs:
            inout = " inout "
            if x["symbol"].__v_classType__ == v_classType_t.transition_t:
                pass
            elif x["symbol"]._varSigConst != varSig.variable_t:
                inout = " in "

            if IsFunction:
                inout = "  "
                

            
            line = "self" +x["suffix"] + " : " + inout + x["symbol"].get_type()  + suffix
            content.append(line)

        
        
        ret=join_str(
            content, 
            Delimeter="; "
            )
        
        return ret


    def impl_get_attribute(self,obj, attName, parent =None):
        attName = str(attName)

        

        xs = hdl.extract_conversion_types(obj)
           
        for x in xs:
            for y in x["symbol"].getMember():
                if y["name"] == attName:
                    return obj.get_vhdl_name() + x["suffix"] + "." +   attName


           
        return obj.get_vhdl_name() + "." +str(attName)
   
    def impl_process_header(self,obj):

        

        ret = []

        for x in hdl.get_extractedTypes(obj): 
            ret += x.impl_process_header(obj)
        
        
        ret=join_str(
            ret, 
            LineBeginning="  "
            )

        
        return ret




    def get_NameMaster2Slave(self,obj):
        return obj._type + "_m2s"

    def get_NameSlave2Master(self,obj):
        return obj._type + "_s2m"

    def get_NameSignal(self,obj):
        return obj._type + "_sig"

    def get_type_simple(self,obj):

        objTypeName = obj._type
        MemberTypeNames = []

        for x in obj.getMember():
            if x["symbol"].__isFreeType__:
                continue
            MemberTypeNames.append(hdl.get_type_simple_template(x["symbol"]))

        ret = make_object_name(objTypeName,MemberTypeNames)
        return ret 







    def extract_conversion_types(self, obj, exclude_class_type=None,filter_inout=None):
        ret =[]

        
        ret.append({ "suffix":"", "symbol": obj})

        ret1 = [
            x for x in ret
            if not( x["symbol"]._issubclass_("v_class")  and exclude_class_type and x["symbol"].__v_classType__ == exclude_class_type)
            if not(filter_inout and x["symbol"]._Inout != filter_inout)
        ]
         

        return ret1


    

    def to_arglist_self(self,obj, name,parent,element, withDefault = False, astParser=None):
        ret = []
        inoutstr =  " in " # fixme 
        varSignal = " Signal "

        if element["symbol"]._varSigConst == varSig.variable_t:
            inoutstr =  " inout " # fixme 
            varSignal = ""

        Default_str = ""
        if withDefault and obj.__writeRead__ != InOut_t.output_t and obj._Inout != InOut_t.output_t:
            Default_str =  " := " + hdl.get_default_value(obj)

        ret.append(varSignal + name + element["suffix"] + " : " + inoutstr +" " +  element["symbol"].getType() +Default_str)
        return ret

    def to_arglist_signal(self,obj, name,parent,element, withDefault = False, astParser=None):
        ret = []
        if element["symbol"]._varSigConst != varSig.signal_t:
            return ret



        members = element["symbol"].getMember()
        for m in members:
            inout = astParser.get_function_arg_inout_type(m["symbol"])
        
            if inout != InOut_t.output_t:
                continue
            ret.append(hdl.to_arglist(
                    m["symbol"], 
                    name + element["suffix"]+"_"+m["name"],
                    None ,
                    withDefault=withDefault,
                    astParser=astParser
                ))
        
        return ret

    def to_arglist(self,obj, name,parent, withDefault = False, astParser=None):
        ret = []
        
        xs = hdl.extract_conversion_types(obj)

        for x in xs:
            ret += self.to_arglist_self(
                    obj, 
                    name,
                    parent,
                    element=x, 
                    withDefault = withDefault, 
                    astParser=astParser
                )
            ret += self.to_arglist_signal(
                    obj, 
                    name,
                    parent,
                    element=x, 
                    withDefault = withDefault, 
                    astParser=astParser
                )


        r =join_str(ret,Delimeter="; ",IgnoreIfEmpty=True)
        return r
    def get_inout_type_recursive(self, obj):
        if obj._varSigConst != varSig.variable_t:
            if  obj._Inout != InOut_t.Internal_t:
                return obj._Inout
            return obj.__writeRead__  

        mem = obj.getMember()
        obj.__writeRead__ = obj._Inout
        for m in mem:
            if hdl.get_inout_type_recursive(m["symbol"]) == InOut_t.input_t:
                obj._add_input()
            elif hdl.get_inout_type_recursive(m["symbol"]) == InOut_t.output_t:
                obj._add_output()

        return obj.__writeRead__

add_primitive_hdl_converter("v_class",v_class_converter )
