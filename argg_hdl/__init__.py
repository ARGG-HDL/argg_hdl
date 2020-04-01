import argg_hdl.argg_hdl_base as ahb
import argg_hdl.argg_hdl_v_symbol as ah_symbol

import argg_hdl.argg_hdl_v_list as ah_list

import argg_hdl.argg_hdl_v_entity as ah_entity
import argg_hdl.argg_hdl_v_entity_list as ah_entity_list

import argg_hdl.argg_hdl_v_class  as ah_v_class
import argg_hdl.argg_hdl_v_enum  as ah_v_enum

import argg_hdl.argg_hdl_simulation  as ah_simulation

import argg_hdl.argg_hdl_v_Package  as ah_v_package

## argg_hdl_base
base0                 = ahb.argg_hdl_base0
base                  = ahb.argg_hdl_base
architecture          = ahb.architecture
end_architecture      = ahb.end_architecture
InOut_t               = ahb.InOut_t
varSig                = ahb.varSig
v_classType_t         = ahb.v_classType_t
v_variable            = ahb.v_variable
v_signal              = ahb.v_signal
v_const               = ahb.v_const                      
port_out              = ahb.port_out          
variable_port_out     = ahb.variable_port_out                  
port_in               = ahb.port_in      
variable_port_in      = ahb.variable_port_in                  
port_Master           = ahb.port_Master          
variable_port_Master  = ahb.variable_port_Master                      
signal_port_Master    = ahb.signal_port_Master                  
port_Stream_Master    = ahb.port_Stream_Master                  
signal_port_Slave     = ahb.signal_port_Slave                  
port_Slave            = ahb.port_Slave          
variable_port_Slave   = ahb.variable_port_Slave                  
port_Stream_Slave     = ahb.port_Stream_Slave                  



v_symbol = ah_symbol.v_symbol



## argg_hdl_v_symbol
v_bool = ah_symbol.v_bool
v_sl = ah_symbol.v_sl
v_slv = ah_symbol.v_slv
v_int  = ah_symbol.v_int

## argg_hdl_v_list
v_list = ah_list.v_list

## argg_hdl_v_entity
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


## v_entity_list

v_entity_list = ah_entity_list.v_entity_list

## argg_hdl_v_class
v_class = ah_v_class.v_class

## argg_hdl.argg_hdl_simulation 
gsimulation = ah_simulation.gsimulation

## argg_hdl.argg_hdl_v_enum 
v_enum = ah_v_enum.v_enum

## argg_hdl.argg_hdl_v_Package
v_package = ah_v_package.v_package