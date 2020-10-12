from argg_hdl.ast.ast_classes.ast_base import v_ast_base, add_class,gIndent
from argg_hdl.ast.ast_classes.ast_type_to_bool import v_type_to_bool

class v_if(v_ast_base):
    def __init__(self,ifEsleIfElse, test, body,oreEsle):
        self.ifEsleIfElse = ifEsleIfElse    
        self.test=test
        self.body = body
        self.oreEsle  = oreEsle
        self.isElse = False


    def __str__(self):
        
        if self.isElse:
            gIndent.deinc()
            ret ="\n" +str(gIndent) +  "elsif ("
            gIndent.inc()
        else:
            ret ="\n" +str(gIndent) +  "if ("
        
            gIndent.inc()
        
        ret += str(self.test) +") then \n"+str(gIndent)
        for x in self.body:
            x_str =str(x)
            if x_str:
               # x_str.replace("\n","\n  ")
                ret += x_str +";\n"+str(gIndent)

        
        oreelse =""
        if len(self.oreEsle) > 0 and type(self.oreEsle[0]).__name__ != "v_if":
            gIndent.deinc()
            oreelse+="\n"+ str(gIndent) + "else"
            gIndent.inc()
            oreelse += "\n"+str(gIndent) 
            for x in self.oreEsle:
                oreelse += str(x)+";\n"+str(gIndent) 
        
        else:
            for x in self.oreEsle:
                x.isElse = True
                oreelse += str(x)
            

        ret += oreelse
        gIndent.deinc()
        if self.isElse:
            ret +=""
        else:
            ret +="\n" +str(gIndent) +  "end if" 
        

        return ret


def body_if(astParser,Node):
    
    ifEsleIfElse = "if"
    test =v_type_to_bool(astParser, astParser.Unfold_body(Node.test))
    body = astParser.Unfold_body(Node.body)
    localContext = astParser.Context
    oreEsle = list ()
    astParser.Context  = oreEsle
    for x in Node.orelse:
        oreEsle.append(astParser.Unfold_body(x))
    astParser.Context =localContext 
    return v_if(ifEsleIfElse, test, body,oreEsle)


add_class("If",body_if)