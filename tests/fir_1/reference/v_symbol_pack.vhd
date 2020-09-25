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


    subtype slv6 is std_logic_vector(5 downto 0);
    constant slv6_null : slv6 := (others => '0');
    type slv6_a is array (natural range <>) of slv6;
    function slv6_ctr(Data : Integer) return slv6;


    subtype slv8 is std_logic_vector(7 downto 0);
    constant slv8_null : slv8 := std_logic_vector(to_unsigned(1, 8));
    type slv8_a is array (natural range <>) of slv8;
    function slv8_ctr(Data : Integer) return slv8;


    subtype signed8 is signed(7 downto 0);
    constant signed8_null : signed8 := (others => '0');
    type signed8_a is array (natural range <>) of signed8;
    function signed8_ctr(Data : Integer) return signed8;


    subtype signed16 is signed(15 downto 0);
    constant signed16_null : signed16 := (others => '0');
    type signed16_a is array (natural range <>) of signed16;
    function signed16_ctr(Data : Integer) return signed16;


    subtype signed17 is signed(16 downto 0);
    constant signed17_null : signed17 := (others => '0');
    type signed17_a is array (natural range <>) of signed17;
    function signed17_ctr(Data : Integer) return signed17;


    subtype signed18 is signed(17 downto 0);
    constant signed18_null : signed18 := (others => '0');
    type signed18_a is array (natural range <>) of signed18;
    function signed18_ctr(Data : Integer) return signed18;




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

            
    function slv6_ctr(Data : Integer) return  slv6 is 
    variable ret : slv6;
    begin;
        ret := std_logic_vector_ctr(Data , slv6'length)
        return ret;
    end function;     

            
    function slv8_ctr(Data : Integer) return  slv8 is 
    variable ret : slv8;
    begin;
        ret := std_logic_vector_ctr(Data , slv8'length)
        return ret;
    end function;     

            
    function signed8_ctr(Data : Integer) return  signed8 is 
    variable ret : signed8;
    begin;
        ret := signed_ctr(Data , signed8'length)
        return ret;
    end function;     

            
    function signed16_ctr(Data : Integer) return  signed16 is 
    variable ret : signed16;
    begin;
        ret := signed_ctr(Data , signed16'length)
        return ret;
    end function;     

            
    function signed17_ctr(Data : Integer) return  signed17 is 
    variable ret : signed17;
    begin;
        ret := signed_ctr(Data , signed17'length)
        return ret;
    end function;     

            
    function signed18_ctr(Data : Integer) return  signed18 is 
    variable ret : signed18;
    begin;
        ret := signed_ctr(Data , signed18'length)
        return ret;
    end function;     

            
end package body;
