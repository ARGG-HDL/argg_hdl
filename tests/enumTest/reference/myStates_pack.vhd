
library IEEE;
library work;
use IEEE.numeric_std.all;
use IEEE.std_logic_1164.all;
use ieee.std_logic_unsigned.all;
use work.argg_hdl_core.all;

package myStates_pack is 

  type myStates is ( 
    e_idle,
    e_running_1,
    e_running_2,
    some_other_state,
    some_other_state2
  );


end myStates_pack;


package body myStates_pack is

end  myStates_pack;

