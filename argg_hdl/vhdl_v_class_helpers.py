from argg_hdl.argg_hdl_base import v_classType_t,varSig,InOut_t,join_str,argg_hdl_base

def _get_connector(symb):
    if symb._Inout == InOut_t.Master_t:
        n_connector = symb.__receiver__[-1]
    else :
        n_connector = symb.__Driver__
    
    return n_connector


class vhdl__Pull_Push():
    def __init__(self,obj, inout):
        self.obj = obj
        self.Inout = inout
        
    def get_selfHandles(self):
        selfHandles = []
        xs = self.obj.__hdl_converter__.extract_conversion_types(self.obj)
        for x in xs:
            arg = "self"+x["suffix"] + "  =>  " +str(self.obj) + x["suffix"]
            selfHandles.append(arg)
        return selfHandles

    def getConnections(self):
        content = []
        for x in self.obj.getMember( self.Inout,varSig.variable_t):
            n_connector = _get_connector( x["symbol"])
            

            ys =n_connector.__hdl_converter__.extract_conversion_types(
                    n_connector, 
                    exclude_class_type= v_classType_t.transition_t, 
                    filter_inout=self.Inout
                )
            for y in ys:
                content.append(x["name"]+" => "+y["symbol"].get_vhdl_name())

        return content 

    def getConnections_outputs(self):
        content = []
        if not(self.Inout == InOut_t.output_t):
            return content

        members = self.obj.__hdl_converter__.get_internal_connections(self.obj)
        for x in members:
            inout_local =  self.Inout
            if x["type"] == 'sig2var':
                inout_local =  InoutFlip(self.Inout)


                
            sig = x["source"]["symbol"].__hdl_converter__.extract_conversion_types(
                    x["source"]["symbol"],
                    exclude_class_type= v_classType_t.transition_t,
                    filter_inout=inout_local
                )
            connector = "_"
            content.append(self.obj.__hdl_name__+"_sig" + connector + x["source"]["name"]+ sig[0]["suffix"] +" => " +self.obj.__hdl_name__+"_sig."  + x["source"]["name"]+ sig[0]["suffix"])
        
        return content


    def __str__(self):
        if self.obj.__v_classType__  == v_classType_t.Record_t:
            return ""
        content = self.get_selfHandles()


        
        content += self.getConnections()

        content += self.getConnections_outputs()
        
        pushpull= "push"
        if self.Inout == InOut_t.input_t:
            pushpull = "pull"

        ret=join_str(
            content, 
            start="    " + pushpull + "( ",
            end=");\n",
            Delimeter=", "
            )

        if  not self.obj.__hdl_converter__.Has_pushpull_function(self.obj, pushpull):
            return ""
        return ret        



class getHeader():
    def __init__(self, obj, name,parent):
        self.obj = obj
        self.name = name 
        self.parent = parent


    def __str__(self):
        ret = "-------------------------------------------------------------------------\n"
        ret += "------- Start Psuedo Class " +self.obj.getName() +" -------------------------\n"
        
        ts = self.obj.__hdl_converter__.extract_conversion_types(self.obj)
        for t in ts:
            ret +=  self.obj.__hdl_converter__.getHeader_make_record(
                t["symbol"], 
                self.name,
                self.parent,
                t["symbol"]._Inout ,
                t["symbol"]._varSigConst
            )
            ret += "\n\n"
        
        self.obj.__hdl_converter__.make_connection(self.obj,self.name,self.parent)
        
        for x in self.obj.__dict__.items():
            t = getattr(self.obj, x[0])
            if issubclass(type(t),argg_hdl_base) and not t._issubclass_("v_class"):
                ret += t.__hdl_converter__.getHeader(t,x[0],self.obj)

        funlist =[]
        for x in reversed(self.obj.__hdl_converter__.__ast_functions__):
            if "_onpull" in x.name.lower()  or "_onpush" in x.name.lower() :
                continue
            funDeclaration = x.__hdl_converter__.getHeader(x,None,None)
            if funDeclaration in funlist:
                x.isEmpty = True
                continue
            funlist.append(funDeclaration)
            ret +=  funDeclaration


        ret += "------- End Psuedo Class " +self.obj.getName() +" -------------------------\n"
        ret += "-------------------------------------------------------------------------\n\n\n"
        return ret