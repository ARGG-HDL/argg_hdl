from argg_hdl.ast.ast_classes.ast_base import v_ast_base, add_class
import  argg_hdl.argg_hdl_hdl_converter as  hdl


class v_slice(v_ast_base):
    def __init__(self,lower,upper,step):
        super().__init__()
        self.lower = lower
        self.upper = upper
        self.step  = step
        self.reversed  =  False
        self.sourceOBJ  =  None

    def set_source(self,sourceOBJ):
        self.sourceOBJ = sourceOBJ

    def __str__(self):

        if self.upper is None:
            upper = str(hdl.length(self.sourceOBJ)) + " -1 " 
        else:
            upper = str(self.upper) 
            if upper.lstrip('-').isnumeric():
                upper = int(upper)
                if upper < 0 :
                    upper = str(hdl.length(self.sourceOBJ)) + " - " + str( abs(upper - 1))
                else:
                    upper = str(int(upper) - 1 )
            else:
                upper += " - 1 "
        
        if self.reversed:
            return str(self.lower) + " to "  + upper

        return  upper  + "  downto  " + str(self.lower) 

def body_unfold_slice(astParser,Node,keywords=None):
    lower = astParser.Unfold_body( Node.lower) if Node.lower else None
    upper = astParser.Unfold_body( Node.upper) if Node.upper else None
    step = astParser.Unfold_body( Node.step) if Node.step else None
    ret = v_slice(lower, upper, step)
    return ret

add_class( "Slice",body_unfold_slice)