import os
import sys
import inspect


from argg_hdl.argg_hdl_base import *
from argg_hdl.argg_hdl_v_function import *
from argg_hdl.argg_hdl_v_entity_list import *
from argg_hdl.argg_hdl_simulation import *
import argg_hdl.argg_hdl_v_Package as argg_pack
import  argg_hdl.vhdl_v_class_helpers as  vc_helper

import  argg_hdl.argg_hdl_hdl_converter as  hdl




class v_class_converter(hdl_converter_base):
    def __init__(self):
        super().__init__()
        self.__ast_functions__ =list()
        self.archetecture_list = []
        self.functionNameVetoList= []

    def includes(self,obj, name,parent):
        ret = ""
        for x in obj.__dict__.items():
            t = getattr(obj, x[0])
            if issubclass(type(t),argg_hdl_base):
                        
                ret += hdl.includes(t,x[0],obj)
        
        for x in obj.__hdl_converter__.__ast_functions__:
            ret += hdl.includes(x,None,obj)

        ret += "use work."+ hdl.get_type_simple(obj)+"_pack.all;"
        return ret

    def get_packet_file_name(self, obj):
        if obj.__vetoHDLConversion__:
            return ""
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




    def recordMember(self,obj, name,parent,Inout=None):
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
            
        
        

    def recordMemberDefault(self, obj, name,parent,Inout=None):
        
        if not issubclass(type(parent),v_class):
            return []
        
        if obj._Inout == InOut_t.Slave_t:
            Inout = InoutFlip(Inout)
        
        if not( obj._varSigConst == varSig.signal_t and Inout == InOut_t.InOut_tt):
            return name + " => " + obj.__hdl_converter__.get_init_values(obj,InOut_Filter=Inout)
        
        ret = []
        xs = hdl.extract_conversion_types(
            obj,
            exclude_class_type=v_classType_t.transition_t
        )
        for x in xs:
            ret.append(name + x["suffix"] + " => " + x["symbol"].__hdl_converter__.get_init_values(x["symbol"])  )
        return ret
            

        
    def get_init_values(self,obj, parent=None, InOut_Filter=None, VaribleSignalFilter = None,ForceExpand=False):
        if obj.__hdl_useDefault_value__ and ForceExpand == False:
            ret = obj.getType(InOut_Filter) + "_null"
            return ret

        member = obj.getMember()
        Content = [
            hdl.recordMemberDefault(
                x["symbol"], 
                x["name"],
                obj,
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
        

    def make_constant(self, obj, name,parent=None,InOut_Filter=None, VaribleSignalFilter = None):
        TypeName = obj.getType()
        member = obj.getMember()

        defaults  = obj.__hdl_converter__.get_init_values(
            obj=obj,
            parent=parent, 
            InOut_Filter=InOut_Filter, 
            VaribleSignalFilter=VaribleSignalFilter,
            ForceExpand=True
        )   
        ret = "\n  constant " + name + " : " + TypeName + ":= " + defaults +';\n'

        return ret

    def getHeader(self,obj, name,parent):
        if issubclass(type(parent),v_class):
            return ""

        header = vc_helper.getHeader(obj, name,parent)
        return str(header)
        

    def getHeader_make_record(self,obj, name, parent=None, InOut_Filter=None, VaribleSignalFilter = None):
        TypeName = obj.getType()
        member = obj.getMember()
        start= "\ntype "+TypeName+" is record \n"
        end=  """end record;
    
    {Default}

    type {TypeName}_a is array (natural range <>) of {TypeName};
        """.format(
          Default = obj.__hdl_converter__.make_constant(
                obj,
                obj.getType() + "_null" , 
                parent, 
                InOut_Filter,
                VaribleSignalFilter
              ),
          TypeName=TypeName  
        )

        
        Content = [
            hdl.recordMember(x["symbol"],x["name"],obj,InOut_Filter)
            for x in member
        ]
        ret=join_str(Content,start= start ,end= end, IgnoreIfEmpty=True,LineEnding=";\n", LineBeginning="    ")


        return ret

    def make_connection(self, obj, name, parent):
        pass
        




        

    def getBody_onPush(self, obj):
        for x in obj.__hdl_converter__.__ast_functions__:
            if "_onpush" in x.name.lower():
                return x.body
        return ""

    def getBody_onPull(self, obj):
        for x in obj.__hdl_converter__.__ast_functions__:
            if  "_onpull" in x.name.lower() :
                return x.body
        return ""

    def get_before_after_conection(self, obj, InOut_Filter, PushPull):
        beforeConnecting = ""
        AfterConnecting = ""
        
        if PushPull== "push":
            beforeConnecting = obj.__hdl_converter__.getBody_onPush(obj)
            inout = " out "
        else:
            AfterConnecting = obj.__hdl_converter__.getBody_onPull(obj)
            inout = " in "
            
        return beforeConnecting, AfterConnecting, inout


    def getBody(self,obj, name,parent):
        if issubclass(type(parent),v_class):
            return ""
        start  = "-------------------------------------------------------------------------\n"
        start += "------- Start Psuedo Class " +obj.getName() +" -------------------------\n"
        end  = "------- End Psuedo Class " +obj.getName() +" -------------------------\n  "
        end += "-------------------------------------------------------------------------\n\n\n"
  
        
        for x in obj.__dict__.items():
            t = getattr(obj, x[0])
            if issubclass(type(t),argg_hdl_base):
                start += hdl.getBody(t,x[0],obj)

        content2 =  [
            hdl.getBody(x,None,None) 
            for x in obj.__hdl_converter__.__ast_functions__ 
            if not ("_onpull" in x.name.lower()   or  "_onpush" in x.name.lower() )
        ]


        ret=join_str(content2, start=start,end=end)
        
        

        return ret
    
    def _vhdl__DefineSymbol(self, obj ,VarSymb=None):
        print_cnvt("_vhdl__DefineSymbol is deprecated")
        if not VarSymb:
            VarSymb = get_varSig(obj._varSigConst)

        if obj.__Driver__ and str( obj.__Driver__) != 'process':
            return ""

        
        return VarSymb +" " +str(obj) + " : " +obj._type +" := " + obj.__hdl_converter__.get_init_values(obj) +";\n"
    

    def get_architecture_header(self, obj):
        ret = []
        xs = hdl.extract_conversion_types(obj)
        for x in xs:
            if  x["symbol"].__v_classType__ ==  v_classType_t.transition_t:
                continue
            if obj._Inout != InOut_t.Internal_t and not obj.__isInst__:
                continue
            if x["symbol"]._varSigConst == varSig.variable_t:
                continue

            VarSymb = get_varSig(x["symbol"]._varSigConst)

            ret.append(VarSymb + " " +x["symbol"].get_vhdl_name() + " : " + x["symbol"]._type+" := " + x["symbol"].__hdl_converter__.get_init_values(x["symbol"]) +";\n")
        
        for x in obj.__hdl_converter__.archetecture_list:
            ret.append( hdl.get_architecture_header(x["symbol"]))

        ret=join_str(
            ret, 
            LineBeginning="  "
            )


        return ret
        
    def get_architecture_body(self, obj):
        primary = hdl.get_primary_object(obj)
        obj.__hdl_converter__ = primary.__hdl_converter__
        ret = []
        for x in obj.__hdl_converter__.archetecture_list:
            ret.append(hdl .get_architecture_body(x["symbol"]))
        
        ret=join_str(
            ret, 
            LineBeginning="  "
            )
        ret=ret.replace("!!SELF!!",str(obj.__hdl_name__))
        return ret


    def get_port_list(self,obj):
        ret = []
        xs = hdl.extract_conversion_types(obj,
            exclude_class_type= v_classType_t.transition_t
        )
        for x in xs:
            inoutstr = " : "+ hdl.InOut_t2str(x["symbol"]) +" "
            ret.append( x["symbol"].get_vhdl_name()+ inoutstr +x["symbol"]._type + " := " +  x["symbol"].__hdl_converter__.get_init_values(x["symbol"])  )
    
        return ret


    def _vhdl_make_port(self, obj, name):
        ret = []

        xs = hdl.extract_conversion_types(obj, 
                exclude_class_type= v_classType_t.transition_t
            )
        for x in xs:
            ret.append( name + x["suffix"] + " => " + x["symbol"].get_vhdl_name())

        return ret


           
    


           
        
    def _vhdl__Pull(self,obj):
        Pull_Push_handle = vc_helper.vhdl__Pull_Push(obj,InOut_t.input_t)
        return str(Pull_Push_handle)


    def _vhdl__push(self,obj):
        Pull_Push_handle = vc_helper.vhdl__Pull_Push(obj,InOut_t.output_t)
        return str(Pull_Push_handle)


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
                ret.append(PushPull+"(self." + x["name"]+", "+PushPullPrefix + x["name"] +");")
        return ret      
         
 
    def _vhdl__reasign(self, obj, rhs, astParser=None,context_str=None):
        
        asOp = hdl.get_assiment_op(obj)

        
        if rhs._Inout == InOut_t.Master_t and rhs._varSigConst == varSig.signal_t:
            raise Exception("cannot read from Master")
        if rhs._Inout == InOut_t.output_t and rhs._varSigConst == varSig.signal_t:
            raise Exception("cannot read from Output")


        obj._add_output()
        
        if obj.__v_classType__ == v_classType_t.Master_t or obj.__v_classType__ == v_classType_t.Slave_t:
            hdl_call = hdl._vhdl__call_member_func(obj, "__lshift__",[obj, rhs],astParser)
            if hdl_call is None:
                astParser.Missing_template=True
                return "-- $$ template missing $$"
            return hdl_call


            
        if rhs._type != obj._type:
            raise Exception("cannot assigne different types.", str(obj), rhs._type, obj._type )
        return obj.get_vhdl_name() + asOp +  rhs.get_vhdl_name()
    
    def _vhdl__reasign_rshift_(self, obj, rhs, astParser=None,context_str=None):
        if obj.__v_classType__ == v_classType_t.Master_t or obj.__v_classType__ == v_classType_t.Slave_t:
            hdl_call = hdl._vhdl__call_member_func(obj, "__rshift__",[obj, rhs],astParser)
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


    def _vhdl_get_attribute(self,obj, attName):
        attName = str(attName)

        

        xs = hdl.extract_conversion_types(obj)
           
        for x in xs:
            for y in x["symbol"].getMember():
                if y["name"] == attName:
                    return obj.get_vhdl_name() + x["suffix"] + "." +   attName


           
        return obj.get_vhdl_name() + "." +str(attName)
   
    def get_process_header(self,obj):

        
        ret = ""
        if obj._Inout != InOut_t.Internal_t:
            return ""
        
        xs = hdl.extract_conversion_types(obj)
        for x in xs:
            if x["symbol"]._varSigConst != varSig.variable_t:
                continue

            VarSymb = get_varSig(x["symbol"]._varSigConst)
            ret += VarSymb +" " +str(x["symbol"]) + " : " +x["symbol"]._type +" := " +  x["symbol"].__hdl_converter__.get_init_values(x["symbol"])  +";\n"

        return ret




    def get_NameMaster2Slave(self,obj):
        return obj._type + "_m2s"

    def get_NameSlave2Master(self,obj):
        return obj._type + "_s2m"

    def get_NameSignal(self,obj):
        return obj._type + "_sig"

    def get_type_simple(self,obj):
        return obj._type







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

class v_class(argg_hdl_base):

    def __init__(self,Name=None,varSigConst=None):
        super().__init__()
        self.__hdl_converter__ = v_class_converter()
        Name = get_value_or_default( Name , type(self).__name__)


        self._type = Name
        self.__v_classType__ = v_classType_t.transition_t 


        self.__vectorPush__ = False
        self.__vectorPull__ = False
        self.__vetoHDLConversion__ = False
        self.__hdl_useDefault_value__ = True
        self.__hdl_name__ =None
        self.__Driver__ = None


        
        if not varSigConst:
            varSigConst = getDefaultVarSig()
        self._varSigConst = varSigConst

        self.__inout_register__ = {}

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

    
    def getMember(self,InOut_Filter=None, VaribleSignalFilter = None):
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

