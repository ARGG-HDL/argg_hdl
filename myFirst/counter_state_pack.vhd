
library IEEE;
library UNISIM;
library work;
use IEEE.numeric_std.all;
use IEEE.std_logic_1164.all;
use UNISIM.VComponents.all;
use ieee.std_logic_unsigned.all;
use work.argg_hdl_core.all;

package counter_state_pack is 

  type counter_state is ( 
    idle,
    running,
    done
  );


end counter_state_pack;


package body counter_state_pack is

end  counter_state_pack;

