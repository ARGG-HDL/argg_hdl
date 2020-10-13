from argg_hdl.ast.ast_classes.ast_base import v_ast_base, add_class

def isDecoratorName(dec, Name):
    if len(dec) == 0:
        return False
    if hasattr(dec[0], "func"): 
        if hasattr(dec[0].func, "id"):
            return dec[0].func.id== Name
    if hasattr(dec[0], "id"):
        return dec[0].id== Name
    return False


class v_funDef(v_ast_base):
    def __init__(self,BodyList,dec=None):
        self.BodyList=BodyList
        self.dec = dec

    def __str__(self):
        ret = "" 
        for x in self.BodyList:
            if x is None:
                continue 
            x_str =str(x) 
            if x_str:
                x_str = x_str.replace("\n", "\n  ")
                ret += x_str+";\n  "

        return ret

    def get_type(self):
        for x in self.BodyList:
            if type(x).__name__ == "v_return":
                return x.get_type()
    





def body_unfold_functionDef(astParser,Node):
    astParser.FuncArgs.append(
        {
            "name":Node.name,
            "symbol": Node.name,
            "ScopeType": ""
        }
    )
    if isDecoratorName(Node.decorator_list, "process" ):
        return astParser._Unfold_body["process"](astParser,Node)
        
    if  isDecoratorName(Node.decorator_list, "rising_edge" ):
        return astParser._Unfold_body["rising_edge"](astParser,Node)

    if  isDecoratorName(Node.decorator_list, "timed" ):
        return astParser._Unfold_body["timed"](astParser,Node)
        
    if isDecoratorName(Node.decorator_list, "combinational" ):
        return astParser._Unfold_body["combinational"](astParser,Node) 
        
    if isDecoratorName(Node.decorator_list, "architecture" ):
        return astParser._Unfold_body["architecture"](astParser,Node) 
    
    if isDecoratorName(Node.decorator_list, "hdl_export" ):
        decorator_l = []
    else:
        decorator_l = astParser.Unfold_body(Node.decorator_list)
    
    localContext = astParser.Context

    ret = list()
    astParser.Context = ret
    for x in Node.body:
        ret.append( astParser.Unfold_body(x))
        

    astParser.Context = localContext
    return v_funDef(ret,decorator_l)


add_class("FunctionDef",body_unfold_functionDef)
