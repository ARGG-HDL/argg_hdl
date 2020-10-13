from argg_hdl.ast.ast_classes.ast_base import v_ast_base, add_class
import  argg_hdl.argg_hdl_hdl_converter as  hdl
from argg_hdl.argg_hdl_lib_enums import getDefaultVarSig, setDefaultVarSig,varSig
from argg_hdl.ast.ast_classes.ast_function_process import  body_unfold_porcess

from argg_hdl.argg_hdl_base_helpers import join_str

class v_process_body_Def(v_ast_base):
    def __init__(self,BodyList,name,LocalVar,dec=None):
        self.BodyList=BodyList
        self.dec = dec
        self.name = name
        self.LocalVar = LocalVar

    def get_local_var(self):
        for x in self.LocalVar:
            if x._type == "undef":
                continue
            yield x

    def get_sensitivity_list(self):
        ret =[str(self.dec[0].argList[0])]
        ret += [
            hdl.impl_process_sensitivity_list(x)
            for x in self.get_local_var()
        ]
        ret = join_str(ret,Delimeter=", ",IgnoreIfEmpty=True)
        return ret

    def get_combinatorial_pull(self):
        ret =[
             hdl.impl_process_pull(x,str(self.dec[0].argList[0]))
            for x in self.get_local_var()
        ]
        ret = join_str(ret,LineBeginning="  ",LineEnding=";\n",IgnoreIfEmpty=True)
        return ret
    def get_combinatorial_push(self):
        ret =[
            hdl.impl_process_push(x,str(self.dec[0].argList[0]))
            for x in self.get_local_var()
        ]
        ret = join_str(ret,LineBeginning="  ",LineEnding=";\n",IgnoreIfEmpty=True)
        return ret


    def impl_process_header(self):
        process_header = ""
        for x in self.LocalVar:
            process_header += hdl.impl_process_header(x)
        return process_header

    def get_body(self):
        body = ""
        for x in self.BodyList:
            x_str =str(x) 
            if x_str:
                x_str = x_str.replace("\n", "\n  ")
                body += x_str+";\n  "
        return body

    def get_process_decorator(self):
        process_decorator = self.dec[0].name +"(" + str(self.dec[0].argList[0])+")"
        return process_decorator

    def __str__(self):

        sensitivity_list = self.get_sensitivity_list()
        process_header = self.impl_process_header()
        body = self.get_body() 
        process_decorator = self.get_process_decorator()
        combinatorial_pull = self.get_combinatorial_pull()
        combinatorial_push = self.get_combinatorial_push()

        ret = """({sensitivity_list}) is
{process_header}
begin
{combinatorial_pull}
if {process_decorator} then
{body}
end if;
{combinatorial_push}
""".format(
    sensitivity_list=sensitivity_list,
    combinatorial_pull= combinatorial_pull,
    process_decorator=process_decorator,
    process_header=process_header,
    body=body,
    combinatorial_push=combinatorial_push
)
        return ret

        

    
def body_unfold_porcess_body(astParser,Node):
    if astParser.get_scope_name() !="process":
        return body_unfold_porcess(astParser,Node = Node ,Body = Node)
    localContext = astParser.Context
    

    dummy_DefaultVarSig = getDefaultVarSig()
    setDefaultVarSig(varSig.variable_t)
    decorator_l = astParser.Unfold_body(Node.decorator_list)

    ret = list()
    astParser.Context = ret
    for x in Node.body:
        ret.append( astParser.Unfold_body(x))

    astParser.Context = localContext
    setDefaultVarSig(dummy_DefaultVarSig)

    return v_process_body_Def(ret,Node.name,astParser.LocalVar,decorator_l)


add_class("rising_edge",body_unfold_porcess_body)