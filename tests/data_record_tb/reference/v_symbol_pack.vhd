library IEEE;
library work;
use IEEE.numeric_std.all;
use IEEE.std_logic_1164.all;
use ieee.std_logic_unsigned.all;
use work.argg_hdl_core.all;



package v_symbol_pack is 

     subtype slv8 is std_logic_vector(7 downto 0);
    constant slv8_null : slv8 := std_logic_vector(to_unsigned(1, 8));
    type slv8_a is array (natural range <>) of slv8;
    function slv8_ctr(Data : Integer) return slv8;




end package;

package body v_symbol_pack is


    function slv8_ctr(Data : Integer) return  slv8 is 
    variable ret : slv8;
    begin
        ret := std_logic_vector_ctr(Data , slv8'length);
        return ret;
    end function;     

            
end package body;
