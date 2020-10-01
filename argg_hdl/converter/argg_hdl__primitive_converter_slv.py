

from argg_hdl.converter.argg_hdl__primitive_type_converter_base import *


class v_slv_converter(v_symbol_converter):
    primitive_type = "std_logic_vector"

    def __init__(self,inc_str):
        super().__init__(inc_str)

    
    def _vhdl__compare(self,obj :"v_symbol", ops, rhs, astParser):
        astParser.add_read(obj)
        obj._add_input()
        if issubclass(type(rhs),argg_hdl_base):
            astParser.add_read(rhs)
            rhs._add_input()
        
        return str(obj) + " "+ obj.__hdl_converter__.ops2str(ops) +" " +   str(rhs)

    


    def _vhdl__reasign(self, obj:"v_symbol", rhs, astParser=None,context_str=None):
        if astParser:
            astParser.add_write(obj)
        obj._add_output()
        target = str(obj)


        if issubclass(type(rhs),argg_hdl_base0)  and str( obj.__Driver__) != 'process':
            obj.__Driver__ = rhs    

        
        asOp = obj.__hdl_converter__.get_assiment_op(obj)
        if str(rhs) == '0':
            return target + asOp+ " (others => '0')"
        
        if  issubclass(type(rhs),argg_hdl_base):
            if rhs.get_type() == 'integer':
                return  """{dest} {asOp} std_logic_vector(to_unsigned({src}, {dest}'length))""".format(
                    dest=target,
                    src = str(rhs),
                    asOp=asOp
                )

            if rhs.get_type() == 'signed':
                return  """{dest} {asOp} std_logic_vector({src})""".format(
                    dest=target,
                    src = str(rhs),
                    asOp=asOp
                )

            if rhs.get_type() == 'unsigned':
                return  """{dest} {asOp} std_logic_vector({src})""".format(
                    dest=target,
                    src = str(rhs),
                    asOp=asOp
                )
            return target + asOp +  str(rhs.__hdl_converter__._vhdl__getValue(rhs, obj,astParser=astParser)) 
        
        if  type(rhs).__name__=="v_Num":
            return  """{dest} {asOp} std_logic_vector(to_unsigned({src}, {dest}'length))""".format(
                dest=target,
                src = str(rhs.value),
                asOp=asOp
            )

        rhs_str = str(rhs)
        if rhs_str.isnumeric():
            return  """{dest} {asOp} std_logic_vector(to_unsigned({src}, {dest}'length))""".format(
                dest=target,
                src = rhs_str,
                asOp=asOp
            )

        return target + asOp+  str(rhs) 


    def _vhdl_slice(self,obj:"v_symbol",sl,astParser=None):
        astParser.add_read(obj)
        obj._add_input()
        if type(sl).__name__ == "v_slice":
            ret = v_slv( Inout = obj._Inout,varSigConst=obj._varSigConst)
            ret.__hdl_name__ = obj.__hdl_name__+"("+str(sl)+")"
        else:
            ret = v_sl(Inout=obj._Inout, varSigConst=obj._varSigConst)
            index = sl.__hdl_converter__._vhdl__getValue(sl,v_uint())
            ret.__hdl_name__ = obj.__hdl_name__+"("+str(index)+")"
            
            
        return ret

        
        
    def _vhdl__reasign_rshift_(self, obj:"v_symbol", rhs, astParser=None,context_str=None):
        if issubclass(type(obj),argg_hdl_base0) and issubclass(type(rhs),argg_hdl_base0):
            if  "std_logic_vector" in rhs._type:
                rhs._add_output()
                asOp = rhs.__hdl_converter__.get_assiment_op(rhs)            
                return str(rhs)+"("+ str(rhs) +"'range)" +asOp +  str(obj)+"("+ str(rhs) +"'range)" 

        return hdl._vhdl__reasign(rhs, obj,astParser,context_str)

    def get_type_simple(self,obj:"v_symbol"):
        if not self.AliasType:
            return  obj._type

        return self.AliasType
        
        

    def _vhdl__getValue(self,obj:"v_symbol", ReturnToObj=None,astParser=None):
        if astParser:
            astParser.add_read(obj)
        obj._add_input()
        if ReturnToObj.get_type() ==  obj._type:
            return obj
    
        if ReturnToObj.get_type() == "integer" :
            return  "to_integer(signed( " + str(obj)  + "))"
        if ReturnToObj.get_type() == "uinteger":
            return  "to_integer(unsigned( " + str(obj)  + "))"
        return obj


    def get_type_func_arg(self,obj:"v_symbol"):
        return "std_logic_vector"


add_primitive_hdl_converter(v_slv_converter.primitive_type, v_slv_converter )