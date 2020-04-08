import os
import sys
import inspect


from argg_hdl.argg_hdl_base import *
from argg_hdl.argg_hdl_v_function import *
from argg_hdl.argg_hdl_v_entity_list import *
from argg_hdl.argg_hdl_simulation import *
import argg_hdl.argg_hdl_v_Package as argg_pack


def _get_connector(symb):
    if symb._Inout == InOut_t.Master_t:
        n_connector = symb.__receiver__[-1]
    else :
        n_connector = symb.__Driver__
    
    return n_connector


def append_hdl_name(name, suffix):
    ret = ""    
    name_sp = str(name).split("(")
    if len(name_sp) == 2:
        ret = name_sp[0]+suffix+"("+ name_sp[1]
    else:
        ret = name_sp[0]+suffix
    
    return ret

class v_class_converter(hdl_converter_base):
    def __init__(self):
        super().__init__()
        self.__BeforePull__ = ""
        self.__AfterPull__  = ""
        self.__BeforePush__ = ""
        self.__AfterPush__  = ""
        self.__ast_functions__ =list()
        self.archetecture_list = []

    def includes(self,obj, name,parent):
        ret = ""
        for x in obj.__dict__.items():
            t = getattr(obj, x[0])
            if issubclass(type(t),argg_hdl_base):
                        
                ret += t.__hdl_converter__.includes(t,x[0],obj)
        
        for x in obj.__hdl_converter__.__ast_functions__:
            ret += x.__hdl_converter__.includes(x,None,obj)

        ret += "use work."+obj.__hdl_converter__.get_type_simple(obj)+"_pack.all;"
        return ret

    def get_packet_file_name(self, obj):
        if obj.__vetoHDLConversion__:
            return ""
        return obj.__hdl_converter__.get_type_simple(obj)+"_pack.vhd"

    def get_packet_file_content(self, obj):
        PackageName = obj.__hdl_converter__.get_type_simple(obj)+"_pack"
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
        if issubclass(type(parent),v_class):
            if obj._Inout == InOut_t.Slave_t:
                Inout = InoutFlip(Inout)
            if obj._varSigConst == varSig.signal_t and Inout == InOut_t.InOut_tt:
                ret = []
                xs = obj.__hdl_converter__.extract_conversion_types(obj,exclude_class_type=v_classType_t.transition_t)
                for x in xs:
                    ret.append(name + x["suffix"] + " : " + x["symbol"].getType())
                return ret
            
            return name + " : " +obj.getType(Inout)
        return []

    def recordMemberDefault(self, obj, name,parent,Inout=None):
        
        if issubclass(type(parent),v_class):
            if obj._Inout == InOut_t.Slave_t:
                Inout = InoutFlip(Inout)
            if obj._varSigConst == varSig.signal_t and Inout == InOut_t.InOut_tt:
                ret = []
                xs = obj.__hdl_converter__.extract_conversion_types(obj,exclude_class_type=v_classType_t.transition_t)
                for x in xs:
                    ret.append(name + x["suffix"] + " => " + x["symbol"].getType() + "_null" )
                return ret
            
            return name + " => " + obj.getType(Inout) + "_null"

        return []

    def make_constant(self, obj, name,parent=None,InOut_Filter=None, VaribleSignalFilter = None):
        TypeName = obj.getType()
        member = obj.getMember()
       
        start = "\n  constant " + name + " : " + TypeName + ":= (\n"

        Content = [
            x["symbol"].__hdl_converter__.recordMemberDefault(x["symbol"], x["name"],obj,InOut_Filter) 
            for x in member
        ]
        ret=join_str(Content,start= start ,end=  "\n  );\n",Delimeter=",\n",LineBeginning= "    ", IgnoreIfEmpty=True)

        return ret

    def getHeader(self,obj, name,parent):
        if issubclass(type(parent),v_class):
            return ""
        ret = "-------------------------------------------------------------------------\n"
        ret += "------- Start Psuedo Class " +obj.getName() +" -------------------------\n"
        
        ts = obj.__hdl_converter__.extract_conversion_types(obj)
        for t in ts:
            ret +=  obj.__hdl_converter__.getHeader_make_record(t["symbol"], name,parent,t["symbol"]._Inout ,t["symbol"]._varSigConst)
            ret += "\n\n"
        
        obj.__hdl_converter__.make_connection(obj,name,parent)
        
        for x in obj.__dict__.items():
            t = getattr(obj, x[0])
            if issubclass(type(t),argg_hdl_base) and not issubclass(type(t),v_class):
                ret += t.__hdl_converter__.getHeader(t,x[0],obj)

        funlist =[]
        for x in reversed(obj.__hdl_converter__.__ast_functions__):
            if "_onpull" in x.name.lower()  or "_onpush" in x.name.lower() :
                continue
            funDeclaration = x.__hdl_converter__.getHeader(x,None,None)
            if funDeclaration in funlist:
                x.isEmpty = True
                continue
            funlist.append(funDeclaration)
            ret +=  funDeclaration


        ret += "------- End Psuedo Class " +obj.getName() +" -------------------------\n"
        ret += "-------------------------------------------------------------------------\n\n\n"
        return ret


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
                TypeName+ "_null", 
                parent, 
                InOut_Filter,
                VaribleSignalFilter
              ),
          TypeName=TypeName  
        )

        
        Content = [
            x["symbol"].__hdl_converter__.recordMember(x["symbol"],x["name"],obj,InOut_Filter)
            for x in member
        ]
        ret=join_str(Content,start= start ,end= end, IgnoreIfEmpty=True,LineEnding=";\n", LineBeginning="    ")


        return ret

    def make_connection(self, obj, name, parent):
            
        
        if obj.__v_classType__ == v_classType_t.transition_t:    
            obj.pull          =  obj.__hdl_converter__.getConnecting_procedure(obj, InOut_t.input_t , "pull", procedureName="pull" )
            obj.push          =  obj.__hdl_converter__.getConnecting_procedure(obj, InOut_t.output_t, "push", procedureName="push")
            obj.pull_rev      =  obj.__hdl_converter__.getConnecting_procedure(obj, InOut_t.output_t, "pull", procedureName="pull")
            obj.push_rev      =  obj.__hdl_converter__.getConnecting_procedure(obj, InOut_t.input_t , "push", procedureName="push")
            
        elif obj.__v_classType__ == v_classType_t.Master_t or obj.__v_classType__ == v_classType_t.Slave_t:
   
            obj.pull       =  obj.__hdl_converter__.getConnecting_procedure(obj, InOut_t.input_t , "pull")
            obj.push       =  obj.__hdl_converter__.getConnecting_procedure(obj, InOut_t.output_t, "push")

            if obj.__vectorPull__:
                obj.vpull       =  obj.__hdl_converter__.getConnecting_procedure_vector(obj, InOut_t.input_t , "pull",procedureName="pull")
            if obj.__vectorPush__:
                obj.vpush       =  obj.__hdl_converter__.getConnecting_procedure_vector(obj, InOut_t.output_t, "push",procedureName="push")

        elif obj.__v_classType__ == v_classType_t.Record_t:
            obj.pull       =  obj.__hdl_converter__.getConnecting_procedure_record(obj, "pull")
            obj.push       =  obj.__hdl_converter__.getConnecting_procedure_record(obj, "push")


    def getConnecting_procedure_record(self,obj, PushPull):
        
        if PushPull== "push":
            inout = " out "
            line =  "data_IO  <=  self;"
        else:
            inout = " in "
            line =  "self  := data_IO;"


        TypeName = obj.getType()
        args = "self : inout "+ TypeName + "; signal data_IO : " + inout + " " + TypeName

        ret = v_procedure(
            name=None, 
            argumentList=args , 
            body=line,
            isFreeFunction=True,
            IsEmpty=False
            )

        return ret
    def getConnecting_procedure_vector(self,obj, InOut_Filter,PushPull,procedureName=None):
        
        isEmpty = False
        if PushPull== "push":
            inout = " out "
            isEmpty = obj.push.isEmpty

        else:
            inout = " in "
            isEmpty = obj.pull.isEmpty
       
        argumentList =  obj.__hdl_converter__.getMemberArgs(obj, InOut_Filter,inout,suffix="_a",IncludeSelf = True,PushPull=PushPull).strip()

        
        xs = obj.__hdl_converter__.extract_conversion_types(obj )
        content = []
             

        for x in xs:
            line = "self" + x["suffix"] +" =>  self" + x["suffix"]+"(i)"
            content.append(line)

        members = obj.__hdl_converter__.get_internal_connections(obj)
        for x in members:
            if x["type"] == 'sig2var':
                
                inout_local =  InoutFlip(InOut_Filter)
                if PushPull == "push":
                    
                    sig = x["destination"]["symbol"].__hdl_converter__.extract_conversion_types(
                        x["destination"]["symbol"],
                        exclude_class_type= v_classType_t.transition_t,
                        filter_inout=inout_local
                    )
                    connector = "_"
                    content.append(obj.__hdl_name__+"_sig" + connector + x["source"]["name"]+ sig[0]["suffix"] +" => "  +obj.__hdl_name__+"_sig" + connector + x["source"]["name"]+ sig[0]["suffix"] +"(i)")
            elif x["type"] == 'var2sig':
                inout_local =  InOut_Filter
                if PushPull == "push":
                    sig = x["source"]["symbol"].__hdl_converter__.extract_conversion_types(
                         x["source"]["symbol"],
                        exclude_class_type= v_classType_t.transition_t,
                        filter_inout=inout_local
                    )
                    connector = "_"
                    content.append(obj.__hdl_name__+"_sig" +connector + x["source"]["name"]+ sig[0]["suffix"] +" => "  +obj.__hdl_name__+"_sig" +connector + x["source"]["name"]+ sig[0]["suffix"] +"(i)")
    
        members = obj.getMember(InOut_Filter) 
        args=join_str(content + [
                str(x["name"]) +" => " + str(x["name"]+"(i)")
                for x in members
            ],
            Delimeter= ", ",
            IgnoreIfEmpty=True
            )

            
        ret        = v_procedure(name=procedureName, argumentList=argumentList , body='''
        for i in 0 to self'length - 1 loop
        {PushPull}( {args});
        end loop;
            '''.format(
                PushPull=PushPull,
                args = args
                
            ),
            isFreeFunction=True,
            IsEmpty=isEmpty
            )

        return ret

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


    def getConnecting_procedure(self,obj, InOut_Filter,PushPull, procedureName=None):
        ClassName=None
        beforeConnecting = ""
        AfterConnecting = ""
        classType = obj.getType(InOut_Filter)
        isFreeFunction = False
        
        if PushPull== "push":
            beforeConnecting = obj.__hdl_converter__.getBody_onPush(obj)
            inout = " out "
        else:
            AfterConnecting = obj.__hdl_converter__.getBody_onPull(obj)
            inout = " in "
            
            

        if  obj.__v_classType__ == v_classType_t.transition_t:
            ClassName="IO_data"
            argumentList = "signal " + ClassName +" : " + inout+ classType
        else:
            argumentList = obj.__hdl_converter__.getMemberArgs(obj, InOut_Filter,inout,IncludeSelf = True,PushPull=PushPull)
            isFreeFunction = True

        Connecting = obj.__hdl_converter__.getMemeber_Connect(obj, InOut_Filter,PushPull, ClassName)
        internal_connections = obj.__hdl_converter__.getMember_InternalConnections(obj, InOut_Filter,PushPull)
        Connecting = join_str([Connecting, internal_connections],LineEnding="\n",LineBeginning="    " ,IgnoreIfEmpty = True )

        IsEmpty=len(Connecting.strip()) == 0 and len(beforeConnecting.strip()) == 0 and  len(AfterConnecting.strip()) == 0
        ret        = v_procedure(name=procedureName, argumentList=argumentList , body='''
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
            isFreeFunction=isFreeFunction
            )
        
        return ret

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
                start += t.__hdl_converter__.getBody(t,x[0],obj)

        content2 =  [
            x.__hdl_converter__.getBody(x,None,None) 
            for x in obj.__hdl_converter__.__ast_functions__ 
            if not ("_onpull" in x.name.lower()   or  "_onpush" in x.name.lower() )
        ]


        ret=join_str(content2, start=start,end=end)
        
        

        return ret
    
    def _vhdl__DefineSymbol(self, obj ,VarSymb=None):
        print("_vhdl__DefineSymbol is deprecated")
        if not VarSymb:
            VarSymb = get_varSig(obj._varSigConst)

        if obj.__Driver__ and str( obj.__Driver__) != 'process':
            return ""
        t = obj.getTypes()
        if len(t) ==3 and obj.__v_classType__ ==  v_classType_t.transition_t:
            ret = ""
            ret += VarSymb + " " +str(obj) + "_m2s : " + t["m2s"] +" := " + t["m2s"]+"_null;\n"
            ret += VarSymb + " " +str(obj) + "_s2m : " + t["s2m"] +" := " + t["s2m"]+"_null;\n"
            return ret

        return VarSymb +" " +str(obj) + " : " +obj._type +" := " + obj._type+"_null;\n"
    

    def get_architecture_header(self, obj):
        ret = []
        xs = obj.__hdl_converter__.extract_conversion_types(obj)
        for x in xs:
            if  x["symbol"].__v_classType__ ==  v_classType_t.transition_t:
                continue
            if obj._Inout != InOut_t.Internal_t and not obj.__isInst__:
                continue
            if x["symbol"]._varSigConst == varSig.variable_t:
                continue

            VarSymb = get_varSig(x["symbol"]._varSigConst)

            ret.append(VarSymb + " " +x["symbol"].get_vhdl_name() + " : " + x["symbol"]._type+" := " + x["symbol"]._type+"_null;\n")
        
        for x in obj.__hdl_converter__.archetecture_list:
            ret.append(x["symbol"].__hdl_converter__.get_architecture_header(x["symbol"]))

        ret=join_str(
            ret, 
            LineBeginning="  "
            )


        return ret
        
    def get_architecture_body(self, obj):
        ret = []
        for x in obj.__hdl_converter__.archetecture_list:
            ret.append(x["symbol"].__hdl_converter__.get_architecture_body(x["symbol"]))
        
        ret=join_str(
            ret, 
            LineBeginning="  "
            )
        ret=ret.replace("!!SELF!!",str(obj.__hdl_name__))
        return ret


    def get_port_list(self,obj):
        ret = []
        xs = obj.__hdl_converter__.extract_conversion_types(obj)
        for x in xs:
            if x["symbol"].__v_classType__ ==  v_classType_t.transition_t:
                continue
            inoutstr = " : "+ x["symbol"].__hdl_converter__.InOut_t2str(x["symbol"]) +" "
            ret.append( x["symbol"].get_vhdl_name()+ inoutstr +x["symbol"]._type + " := " + x["symbol"]._type + "_null")
    
        return ret


    def _vhdl_make_port(self, obj, name):
        ret = []

        xs =obj.__hdl_converter__.extract_conversion_types(obj, 
                exclude_class_type= v_classType_t.transition_t
            )
        for x in xs:
            ret.append( name + x["suffix"] + " => " + x["symbol"].get_vhdl_name())

        return ret


           
    

    def __vhdl__Pull_Push(self, obj, Inout):
        if obj.__v_classType__  == v_classType_t.Record_t:
            return ""
        selfHandles = []
        xs = obj.__hdl_converter__.extract_conversion_types(obj)
        for x in xs:
            arg = "self"+x["suffix"] + "  =>  " +str(obj) + x["suffix"]
            selfHandles.append(arg)

        
        content = []
        for x in obj.getMember( Inout,varSig.variable_t):
            n_connector = _get_connector( x["symbol"])
            

            ys =n_connector.__hdl_converter__.extract_conversion_types(n_connector, 
                    exclude_class_type= v_classType_t.transition_t, filter_inout=Inout
                )
            for y in ys:
                content.append(x["name"]+" => "+y["symbol"].get_vhdl_name())
        
        #content = [ 
        #    x["name"]+" => "+x["symbol"].__hdl_converter__._get_connector_name(x["symbol"], Inout)
        #    for x in obj.getMember( Inout,varSig.variable_t) 
        #]
        if Inout == InOut_t.output_t:
            members = obj.__hdl_converter__.get_internal_connections(obj)
            for x in members:
                if x["type"] == 'sig2var':
                
                    inout_local =  InoutFlip(Inout)
                    sig = x["destination"]["symbol"].__hdl_converter__.extract_conversion_types(
                            x["destination"]["symbol"],
                            exclude_class_type= v_classType_t.transition_t,
                            filter_inout=inout_local
                        )
                    connector = "_"
                    content.append(obj.__hdl_name__+"_sig" + connector + x["source"]["name"]+ sig[0]["suffix"] +" => " +obj.__hdl_name__+"_sig."  + x["source"]["name"]+ sig[0]["suffix"])
                elif x["type"] == 'var2sig':
                    inout_local =  Inout
                    sig = x["source"]["symbol"].__hdl_converter__.extract_conversion_types(
                            x["source"]["symbol"],
                            exclude_class_type= v_classType_t.transition_t,
                            filter_inout=inout_local
                        )
                    connector = "_"
                    content.append(obj.__hdl_name__+"_sig" + connector + x["source"]["name"]+ sig[0]["suffix"] +" => " +obj.__hdl_name__+"_sig."  + x["source"]["name"]+ sig[0]["suffix"])

        pushpull= "push"
        if Inout == InOut_t.input_t:
            pushpull = "pull"

        ret=join_str(
            selfHandles+content, 
            start="    " + pushpull + "( ",
            end=");\n",
            Delimeter=", "
            )

        if  not obj.__hdl_converter__.Has_pushpull_function(obj, pushpull):
            return ""
        return ret        
        
    def _vhdl__Pull(self,obj):

        return obj.__hdl_converter__.__vhdl__Pull_Push(obj,InOut_t.input_t)

    def _vhdl__push(self,obj):


        return obj.__hdl_converter__.__vhdl__Pull_Push(obj,InOut_t.output_t)

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

   
    def getMemberArgsImpl(self, obj, InOut_Filter,InOut,suffix="",PushPull=""):
        members = obj.getMember(InOut_Filter) 
        members_args = list()
        
        for i in members:
            if i["symbol"]._Inout == InOut_t.Slave_t:
                inout_local =  InoutFlip(InOut_Filter)
            else:
                inout_local = InOut_Filter 




            if issubclass(type(i["symbol"]),v_class)   and  i["symbol"].__v_classType__ == v_classType_t.Master_t:
                members_args.append( i["symbol"].__hdl_converter__.getMemberArgsImpl( i["symbol"], inout_local,InOut) )
            
            else:
                members_args.append({ 
                    "name" :  i["name"], 
                    "symbol" : i["symbol"].getType(inout_local),
                    "vhdl_name": i["symbol"].get_vhdl_name(inout_local)
                    })
            
        return members_args

    def getMemberArgs(self,obj, InOut_Filter,InOut,suffix="", IncludeSelf =False,PushPull=""):
        members_args = []
        
        if IncludeSelf:
            xs = obj.__hdl_converter__.extract_conversion_types(obj )
            for x in xs:
                varsig = " "
                self_InOut = " inout "
                if x["symbol"]._varSigConst == varSig.signal_t :
                    varsig = " signal "
                    self_InOut = " in "  
                members_args.append(varsig + "self" + x["suffix"]  + " : " + self_InOut + " "  + x["symbol"].getType()+suffix)
            if PushPull == "push":
                i_members = obj.__hdl_converter__.get_internal_connections(obj)
                for m in i_members:
                    if m["type"] == 'sig2var':
                        sig = m["source"]["symbol"].__hdl_converter__.extract_conversion_types(
                            m["source"]["symbol"],
                            exclude_class_type= v_classType_t.transition_t,
                            filter_inout=InoutFlip(InOut_Filter)
                        )
                        
                        members_args.append(varsig + "self_sig_" +  m["source"]["name"] + sig[0]["suffix"]  + " : out "  + sig[0]["symbol"].getType()+suffix)
                    elif m["type"] == 'var2sig':
                        sig = m["source"]["symbol"].__hdl_converter__.extract_conversion_types(
                            m["source"]["symbol"],
                            exclude_class_type= v_classType_t.transition_t,
                            filter_inout=InOut_Filter
                        )
                        
                        members_args.append(varsig + "self_sig_" +  m["source"]["name"] + sig[0]["suffix"]  + " : out "  + sig[0]["symbol"].getType()+suffix)
                            
                    
        
        members = obj.getMember(InOut_Filter,VaribleSignalFilter=varSig.variable_t) 
       
        for i in members:
            n_connector = _get_connector( i["symbol"])
            xs = i["symbol"].__hdl_converter__.extract_conversion_types( i["symbol"], 
                    exclude_class_type= v_classType_t.transition_t, filter_inout=InOut_Filter
                )

            for x in xs:
               
                varsig = " "
                if n_connector._varSigConst == varSig.signal_t :
                    varsig = " signal "
                    
                members_args.append(varsig + i["name"] + " : " + InOut + " "  + x["symbol"].getType()+suffix)
            

        ret=join_str(
            members_args, 
            Delimeter="; "
            )
        return ret    

    def get_internal_connections(self,obj):
        ret = []
        members = obj.getMember() 
        for dest in members:
            d = dest["symbol"].__Driver__
            source = [x for x in members if x["symbol"] is d]
            if source:
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

    def getMember_InternalConnections(self,obj, InOut_Filter,PushPull):
        ret = []

        members = obj.__hdl_converter__.get_internal_connections(obj)
        for x in members:
            if x["type"] == 'sig2var':
                
                inout_local =  InoutFlip(InOut_Filter)
                if PushPull == "pull":
                    sig =x["destination"]["symbol"].__hdl_converter__.extract_conversion_types(
                        x["destination"]["symbol"],
                        exclude_class_type= v_classType_t.transition_t,
                        filter_inout=inout_local
                    )
                    connector = "."
                if PushPull == "push":
                    
                    sig = x["destination"]["symbol"].__hdl_converter__.extract_conversion_types(
                        x["destination"]["symbol"],
                        exclude_class_type= v_classType_t.transition_t,
                        filter_inout=inout_local
                    )
                    connector = "_"
                ret.append(PushPull + "(" +obj.__hdl_name__+"."+x["destination"]["name"] +", "  +obj.__hdl_name__+"_sig" + connector + x["source"]["name"]+ sig[0]["suffix"] +")" )
            elif x["type"] == 'var2sig':
                inout_local =  InOut_Filter
                if PushPull == "pull":
                    sig = x["source"]["symbol"].__hdl_converter__.extract_conversion_types(
                         x["source"]["symbol"],
                        exclude_class_type= v_classType_t.transition_t,
                        filter_inout=inout_local
                    )
                    connector = "."
                if PushPull == "push":
                    sig = x["source"]["symbol"].__hdl_converter__.extract_conversion_types(
                         x["source"]["symbol"],
                        exclude_class_type= v_classType_t.transition_t,
                        filter_inout=inout_local
                    )
                    connector = "_"
                ret.append(PushPull + "(" +obj.__hdl_name__+"."+x["destination"]["name"] +", "  +obj.__hdl_name__+"_sig" +connector + x["source"]["name"]+ sig[0]["suffix"] +");" )
        return ret


    def getMemeber_Connect(self,obj, InOut_Filter,PushPull,ClassName=None):
        ret = []
        if ClassName:
            PushPullPrefix = ClassName + "."
        else:
            PushPullPrefix = ""
            
        members = obj.getMember() 
        
        for x in members:
            if x["symbol"]._Inout == InOut_t.Internal_t:
                continue
            ys =x["symbol"].__hdl_converter__.extract_conversion_types(
                x["symbol"],
                exclude_class_type= v_classType_t.transition_t,
                filter_inout=InOut_Filter)
            for y in ys:
                ret.append(PushPull+"(self." + x["name"]+", "+PushPullPrefix + x["name"] +");")
        return ret      
         
 
    def _vhdl__reasign(self, obj, rhs, astParser=None,context_str=None):
        
        asOp = obj.__hdl_converter__.get_assiment_op(obj)

        
        if rhs._Inout == InOut_t.Master_t:
            raise Exception("cannot read from Master")
        if rhs._Inout == InOut_t.output_t:
            raise Exception("cannot read from Output")

        #if rhs._type != obj._type:
        #    raise Exception("cannot assigne different types.", str(obj), rhs._type, obj._type )

        
        t = obj.getTypes()
        if len(t) ==3 and obj.__v_classType__ ==  v_classType_t.transition_t:
            if rhs._type != obj._type:
                raise Exception("cannot assigne different types.", str(obj), rhs._type, obj._type )
            ret ="---------------------------------------------------------------------\n--  " + obj.get_vhdl_name() +" << " + rhs.get_vhdl_name()+"\n" 
            
            ret += obj.get_vhdl_name(InOut_t.output_t) + asOp + rhs.get_vhdl_name(InOut_t.output_t) +";\n" 
            ret += rhs.get_vhdl_name(InOut_t.input_t) + asOp + obj.get_vhdl_name(InOut_t.input_t)
            return ret 

        obj._add_output()
        
        if obj.__v_classType__ == v_classType_t.Master_t or obj.__v_classType__ == v_classType_t.Slave_t:
            hdl = obj.__hdl_converter__._vhdl__call_member_func(obj, "__lshift__",[obj, rhs],astParser)
            if hdl is None:
                astParser.Missing_template=True
                return "-- $$ template missing $$"
            return hdl


            
        if rhs._type != obj._type:
            raise Exception("cannot assigne different types.", str(obj), rhs._type, obj._type )
        return obj.get_vhdl_name() + asOp +  rhs.get_vhdl_name()
    
    def _vhdl__reasign_rshift_(self, obj, rhs, astParser=None,context_str=None):
        if obj.__v_classType__ == v_classType_t.Master_t or obj.__v_classType__ == v_classType_t.Slave_t:
            hdl = obj.__hdl_converter__._vhdl__call_member_func(obj, "__rshift__",[obj, rhs],astParser)
            if hdl is None:
                astParser.Missing_template=True
                return "-- $$ template missing $$"
            return hdl
        raise Exception("Unsupported r shift", str(obj), rhs._type, obj._type )

    def get_self_func_name(self, obj, IsFunction = False, suffix = ""):
        xs = obj.__hdl_converter__.extract_conversion_types(obj ,filter_inout=InOut_t.Internal_t)
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
        if obj.__v_classType__ == v_classType_t.transition_t and obj._varSigConst != varSig.variable_t:
            for x in obj.getMember():
                if x["name"] == attName:

                    if x["symbol"]._Inout  == InOut_t.output_t:
                        suffix = "_m2s"
                    else:
                        suffix = "_s2m"

                    return obj.get_vhdl_name() + suffix + "." +   attName
        
        if obj._varSigConst == varSig.combined_t:
            xs = obj.__hdl_converter__.extract_conversion_types(obj)
        else:
            xs =[{
                'suffix' : "",
                'symbol' : obj
            }]
            
        for x in xs:
            for y in x["symbol"].getMember():
                if y["name"] == attName:
                    return obj.get_vhdl_name() + x["suffix"] + "." +   attName


           
        return obj.get_vhdl_name() + "." +str(attName)
   
    def get_process_header(self,obj):

        
        ret = ""
        if obj._Inout != InOut_t.Internal_t:
            return ""
        
        xs = obj.__hdl_converter__.extract_conversion_types(obj)
        for x in xs:
            if x["symbol"]._varSigConst != varSig.variable_t:
                continue

            VarSymb = get_varSig(x["symbol"]._varSigConst)
            ret += VarSymb +" " +str(x["symbol"]) + " : " +x["symbol"]._type +" := " + x["symbol"]._type +"_null;\n"

        return ret

    def get_NameMaster(self,obj):
        return obj._type + "_master"

    def get_NameSlave(self,obj):
        return obj._type + "_slave"


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
        
        if obj.__v_classType__ ==  v_classType_t.transition_t:
            
            
            x = v_class(obj.__hdl_converter__.get_NameSlave2Master(obj), obj._varSigConst)
            x.__v_classType__ = v_classType_t.Record_t
            x.__vetoHDLConversion__  = True
            x.__hdl_name__ = append_hdl_name(obj.__hdl_name__,"_s2m")



            x._Inout=InOut_t.input_t
            if obj._Inout == InOut_t.input_t or obj._Inout == InOut_t.Slave_t:
                x._Inout=InOut_t.output_t

            ys= obj.getMember(InOut_t.input_t)
            for y in ys: 
                setattr(x, y["name"], y["symbol"])
            ret.append({ "suffix":"_s2m", "symbol": x})

            x = v_class(obj.__hdl_converter__.get_NameMaster2Slave(obj), obj._varSigConst)
            x.__v_classType__ = v_classType_t.Record_t
            x.__vetoHDLConversion__  = True
            x._Inout=InOut_t.output_t
            
            if obj._Inout == InOut_t.input_t or obj._Inout == InOut_t.Slave_t:
                x._Inout=InOut_t.input_t
                
            
            x.__hdl_name__ = append_hdl_name(obj.__hdl_name__,"_m2s")
            ys= obj.getMember(InOut_t.output_t)
            for y in ys: 
                setattr(x, y["name"], y["symbol"])
            ret.append({ "suffix":"_m2s", "symbol": x})

            ret.append({ "suffix":"", "symbol": obj})
        
        elif obj.__v_classType__ ==  v_classType_t.Master_t or obj.__v_classType__ ==  v_classType_t.Slave_t: 
            x = v_class(obj.__hdl_converter__.get_NameSignal(obj), varSig.signal_t)
            x.__v_classType__ = v_classType_t.Record_t
            x.__vetoHDLConversion__  = True
            x._Inout= obj._Inout
            x.__writeRead__ = obj.__writeRead__
            x.__hdl_name__ = str(obj.__hdl_name__)+"_sig"
            ys= obj.getMember(VaribleSignalFilter=varSig.signal_t)
            if len(ys)>0:
                for y in ys: 
                    setattr(x, y["name"], y["symbol"])
                
                ret.append({ "suffix":"_sig", "symbol": x})

            x = v_class(obj._type, varSig.variable_t)
            x.__v_classType__ = v_classType_t.Record_t
            x.__vetoHDLConversion__  = True
            x._Inout= obj._Inout
            x.__writeRead__ = obj.__writeRead__
            x.__hdl_name__ = obj.__hdl_name__
            ys= obj.getMember(VaribleSignalFilter=varSig.variable_t)
            if len(ys)>0:
                for y in ys: 
                    setattr(x, y["name"], y["symbol"])
                ret.append({ "suffix":"", "symbol": x})

            #ret.append({ "suffix":"", "symbol": obj})
        else:
            ret.append({ "suffix":"", "symbol": obj})

        ret1 = []
         
        for x in ret:
            if x["symbol"]._issubclass_("v_class")  and exclude_class_type and x["symbol"].__v_classType__ == exclude_class_type:
                continue
            if filter_inout and x["symbol"]._Inout != filter_inout:
                continue           
            ret1.append(x)
        return ret1

    def to_arglist(self,obj, name,parent,withDefault = False):
        ret = []
        
        xs = obj.__hdl_converter__.extract_conversion_types(obj)

        for x in xs:
            inoutstr = ""
            varSignal = "signal "
            if x["symbol"]._varSigConst == varSig.variable_t:
                #x["symbol"].__hdl_converter__.get_inout_type_recursive( x["symbol"])

                #inoutstr =  x["symbol"].__hdl_converter__.InOut_t2str( x["symbol"])
                inoutstr =  " inout " # fixme 
                varSignal = ""
            Default_str = ""
            if withDefault and obj.__writeRead__ != InOut_t.output_t and obj._Inout != InOut_t.output_t:
                Default_str =  " := " + obj.__hdl_converter__.get_default_value(obj)

            ret.append(varSignal + name + x["suffix"] + " : " + inoutstr +" " +  x["symbol"].getType() +Default_str)

            if x["symbol"]._varSigConst == varSig.signal_t:
                members = x["symbol"].getMember()
                for m in members:
                    if m["symbol"].__writeRead__ == InOut_t.Internal_t:
                        continue
                    ret.append(m["symbol"].to_arglist(name + x["suffix"]+"_"+m["name"],None ,withDefault=withDefault))

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
            if m["symbol"].__hdl_converter__.get_inout_type_recursive(m["symbol"]) == InOut_t.input_t:
                obj._add_input()
            elif m["symbol"].__hdl_converter__.get_inout_type_recursive(m["symbol"]) == InOut_t.output_t:
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
        
        self.__hdl_name__ =None
        self.__Driver__ = None


        
        if not varSigConst:
            varSigConst = getDefaultVarSig()
        self._varSigConst = varSigConst

    def set_vhdl_name(self,name, Overwrite = False):
        if self.__hdl_name__ and self.__hdl_name__ != name and not Overwrite:
            raise Exception("double Conversion to vhdl")
        
        self.__hdl_name__ = name


        if self._varSigConst == varSig.variable_t:
            mem = self.getMember()
            for x in mem:
                x["symbol"].set_vhdl_name(name+"."+x["name"],Overwrite)
        else:
            xs = self.__hdl_converter__.extract_conversion_types(self, exclude_class_type= v_classType_t.transition_t,)
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
            return append_hdl_name(str(self.__hdl_name__), "_s2m")
        
        if Inout== InOut_t.output_t:
            return append_hdl_name(str(self.__hdl_name__), "_m2s")
        
        return None



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
        if self.__Driver__ and str( self.__Driver__) != 'process':
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

        for i in range(len(self_members)):
            rhs_members[i]['symbol'] << self_members[i]['symbol']
            rhs_members[i]['symbol']._set_to_sub_connection()

        self_members  = self.get_m2s_signals()
        rhs_members  = rhs.get_m2s_signals()
        for i in range(len(self_members)):
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
        self_members = self.getMember()
        for x in self_members:
            x["symbol"]._instantiate_()

        self._Inout = InoutFlip(self._Inout)
        self.__isInst__ = True
        return self
    
    def _un_instantiate_(self, Name = ""):
        self_members = self.getMember()
        for x in self_members:
            x["symbol"]._un_instantiate_(x["name"])
        
        
        self.set_vhdl_name(Name,True)
        self._Inout = InoutFlip(self._Inout)
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

class v_class_master(v_class):

    def __init__(self,Name=None,varSigConst=None):
        super().__init__(Name,varSigConst)
        self.__vectorPush__   = True
        self.__vectorPull__   = True
        self.__v_classType__  = v_classType_t.Master_t
        self._varSigConst       = varSig.combined_t


class v_class_slave(v_class):

    def __init__(self,Name=None,varSigConst=None):
        super().__init__(Name,varSigConst)
        self.__vectorPush__   = True
        self.__vectorPull__   = True
        self.__v_classType__  = v_classType_t.Slave_t
        self._varSigConst       = varSig.combined_t


def get_master(transObj):
    return transObj.get_master()

def get_salve(transObj):
    return transObj.get_slave()

def get_handle(transObj):
    if transObj._Inout == InOut_t.Slave_t:
        return get_salve(transObj)
    
    if transObj._Inout  == InOut_t.Master_t:
        return get_master(transObj)
    
    raise Exception("Unable to determint requiered handle")
