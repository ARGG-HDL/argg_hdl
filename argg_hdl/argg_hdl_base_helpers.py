from  argg_hdl.argg_hdl_lib_enums import *

def get_type(symbol):
    if hasattr(symbol, "get_type"):
        return symbol.get_type()
    if symbol is None:
        return "None"
    if symbol["symbol"] is None:
        return "None"
    return symbol["symbol"].get_type()

def get_symbol(symbol):
    if hasattr(symbol, "get_symbol"):
        return symbol.get_symbol()
    if symbol is None:
        return None 
    if symbol["symbol"] is None:
        return None
    return symbol["symbol"].get_symbol()
    
