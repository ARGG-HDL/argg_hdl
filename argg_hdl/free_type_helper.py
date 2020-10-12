

from argg_hdl.argg_hdl_base import *


class extracted_freeType:
    def __init__(self, symbol, suffix=""):
        self.symbol = symbol
        self.suffix = suffix
    

    def get_symbol(self,obj):
        x = hdl.get_free_symbols(obj,"" )
        x = [y for y in x if y.suffix == self.suffix]
        x = x[0].symbol
        return x

    def getHeader_make_record(self, obj, name):
        return ""


    def get_architecture_header(self, obj):
        x = self.get_symbol(obj)
        
        if x._Inout != InOut_t.Internal_t and not x.__isInst__:
            return []
        if x._varSigConst == varSig.combined_t and x._varSigConst == varSig.variable_t:
            return []
        if x._varSigConst ==  varSig.variable_t:
            return []
        driver,IsInit = x.__Get_Driver_in_scope__()
        if driver is not x:
            return []

        return [ "signal   " + hdl.get_HDL_name(x, obj ,self.suffix)  + " : " + x._type+ " := " + hdl.get_init_values(x) +";\n"]
        

    def get_process_header(self, obj):
        return []


    def def_entity_port(self, obj):
        x = self.get_symbol(obj)
        inout =x._Inout

        if not (inout  == InOut_t.input_t or inout  == InOut_t.output_t ):
            return []       
            
        inoutstr = " : "+ hdl.InOut_t2str2(self.symbol,  inout) +" "
        return [hdl.get_HDL_name(self.symbol, obj, self.suffix) + inoutstr + self.symbol._type + " := " +  hdl.get_init_values(self.symbol) ]
    
    def vhdl_make_port(self, obj, name):
        x = self.get_symbol(obj)
        inout = x._Inout
        if not (inout  == InOut_t.input_t or inout  == InOut_t.output_t ):
            return []

        driver,IsInit = x.__Get_Driver_in_scope__()
        
        if driver is not x:
            return [name + self.suffix + " => " + str( driver )   ]

        return [name + self.suffix + " => " + hdl.get_HDL_name( self.symbol, x ,self.suffix ) ]
            
