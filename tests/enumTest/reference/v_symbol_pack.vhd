library IEEE;
library work;
use IEEE.numeric_std.all;
use IEEE.std_logic_1164.all;
use ieee.std_logic_unsigned.all;
use work.argg_hdl_core.all;



package v_symbol_pack is 

     subtype slv32 is std_logic_vector(31 downto 0);
    constant slv32_null : slv32 := (others => '0');
    type slv32_a is array (natural range <>) of slv32;
    function slv32_ctr(Data : Integer) return slv32;


    subtype slv16 is std_logic_vector(15 downto 0);
    constant slv16_null : slv16 := (others => '0');
    type slv16_a is array (natural range <>) of slv16;
    function slv16_ctr(Data : Integer) return slv16;


    subtype slv11 is std_logic_vector(10 downto 0);
    constant slv11_null : slv11 := (others => '0');
    type slv11_a is array (natural range <>) of slv11;
    function slv11_ctr(Data : Integer) return slv11;


    subtype slv8 is std_logic_vector(7 downto 0);
    constant slv8_null : slv8 := std_logic_vector(to_unsigned(1, 8));
    type slv8_a is array (natural range <>) of slv8;
    function slv8_ctr(Data : Integer) return slv8;




end package;

package body v_symbol_pack is


    function slv32_ctr(Data : Integer) return  slv32 is 
    variable ret : slv32;
    begin;
        ret := std_logic_vector_ctr(Data , slv32'length)
        return ret;
    end function;     

            
    function slv16_ctr(Data : Integer) return  slv16 is 
    variable ret : slv16;
    begin;
        ret := std_logic_vector_ctr(Data , slv16'length)
        return ret;
    end function;     

            
    function slv11_ctr(Data : Integer) return  slv11 is 
    variable ret : slv11;
    begin;
        ret := std_logic_vector_ctr(Data , slv11'length)
        return ret;
    end function;     

            
    function slv8_ctr(Data : Integer) return  slv8 is 
    variable ret : slv8;
    begin;
        ret := std_logic_vector_ctr(Data , slv8'length)
        return ret;
    end function;     

            
end package body;
