-- XGEN: Autogenerated File

library IEEE;
library UNISIM;
library work;
use IEEE.numeric_std.all;
use IEEE.std_logic_1164.all;
use UNISIM.VComponents.all;
use ieee.std_logic_unsigned.all;
use work.argg_hdl_core.all;


entity slice_TB is 
end entity;



architecture rtl of slice_TB is

--------------------------slice_TB-----------------
  signal counter : std_logic_vector := (others => '0'); 
  signal counter2 : std_logic_vector := (others => '0'); 
  signal counter3 : std_logic_vector(31 downto 0) := x"00000001"; 
  signal d0 : std_logic_vector(3 downto 0) := (others => '0'); 
  signal d1 : std_logic_vector(3 downto 0) := (others => '0'); 
  signal d2 : std_logic_vector(3 downto 0) := (others => '0'); 
  signal d3 : std_logic_vector(3 downto 0) := (others => '0'); 
  signal d4 : std_logic_vector(15 downto 0) := (others => '0'); 
--------------------------clkgen-----------------
  signal clkgen_clk : std_logic := '0'; 
-------------------------- end clkgen-----------------
-------------------------- end slice_TB-----------------

begin
  -- begin architecture
  
-----------------------------------
proc : process(clkgen_clk) is
  begin
    if rising_edge(clkgen_clk) then 
  counter <= counter + 1;
    counter2(32 downto 15) <= counter(23 downto 1);
    counter3(32 downto 1) <= counter3;
    d4 <= d0 & d1 & d2 & d3;
    
      if (counter = 10) then 
        d0  <=  std_logic_vector(to_unsigned(10, d0'length));
        
      end if;
    
      if (counter = 20) then 
        d1  <=  std_logic_vector(to_unsigned(11, d1'length));
        
      end if;
    
      if (counter = 30) then 
        d2  <=  std_logic_vector(to_unsigned(12, d2'length));
        
      end if;
    
      if (counter = 40) then 
        d3  <=  std_logic_vector(to_unsigned(13, d3'length));
        
      end if;
    end if;
  
  end process;
  -- end architecture

  clkgen : entity work.clk_generator port map (
    clk => clkgen_clk
  );
  
end architecture;