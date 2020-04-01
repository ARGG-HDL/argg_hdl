__all__ = ["argg_hdl_base", "argg_hdl_v_symbol"]
import argg_hdl.argg_hdl_base as ahb
import argg_hdl.argg_hdl_v_symbol as ah_symbol

import argg_hdl.argg_hdl_v_list as ah_list

import argg_hdl.argg_hdl_v_entity as ah_entity

base0 = ahb.argg_hdl_base0
base = ahb.argg_hdl_base
v_symbol = ah_symbol.v_symbol

v_bool = ah_symbol.v_bool
v_sl = ah_symbol.v_sl
v_slv = ah_symbol.v_slv
v_int  = ah_symbol.v_int


v_list = ah_list.v_list

##
process         = ah_entity.process      
timed           = ah_entity.timed        
v_create        = ah_entity.v_create     
wait_for        = ah_entity.wait_for     
combinational   = ah_entity.combinational
v_switch        = ah_entity.v_switch     
v_case          = ah_entity.v_case       
rising_edge     = ah_entity.rising_edge  
v_entity        = ah_entity.v_entity  
v_clk_entity    = ah_entity.v_clk_entity 
