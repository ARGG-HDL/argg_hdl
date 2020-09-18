-- XGEN: Autogenerated File

library IEEE;
library work;
use IEEE.numeric_std.all;
use IEEE.std_logic_1164.all;
use ieee.std_logic_unsigned.all;
use work.argg_hdl_core.all;


package register_t_pack is 

-------------------------------------------------------------------------
------- Start Psuedo Class register_t -------------------------

type register_t is record 
    address : std_logic_vector(15 downto 0);
    value : std_logic_vector(15 downto 0);
end record;
    
    
  constant register_t_null : register_t:= (
    address => (others => '0'),
    value => (others => '0')
  );


    type register_t_a is array (natural range <>) of register_t;
        

  procedure pull (self : inout register_t; signal data_IO :  in  register_t);
  procedure push (self : inout register_t; signal data_IO :  out  register_t);
------- End Psuedo Class register_t -------------------------
-------------------------------------------------------------------------


end register_t_pack;


package body register_t_pack is

-------------------------------------------------------------------------
------- Start Psuedo Class register_t -------------------------
procedure pull (self : inout register_t; signal data_IO :  in  register_t) is
   
  begin 
 self  := data_IO; 
end procedure;

procedure push (self : inout register_t; signal data_IO :  out  register_t) is
   
  begin 
 data_IO  <=  self; 
end procedure;

------- End Psuedo Class register_t -------------------------
  -------------------------------------------------------------------------


end register_t_pack;
