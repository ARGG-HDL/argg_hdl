-- XGEN: Autogenerated File

library IEEE;
library UNISIM;
library work;
use IEEE.numeric_std.all;
use IEEE.std_logic_1164.all;
use UNISIM.VComponents.all;
use ieee.std_logic_unsigned.all;
use work.axisStream_slv32.all;
use work.hlpydlcore.all;
use work.klm_globals_pack.all;
use work.register_t_pack.all;


entity InputDelay_tb is 
end entity;



architecture rtl of InputDelay_tb is

--------------------------InputDelay_tb-----------------
--------------------------clkgen-----------------
  signal clkgen_clk : std_logic := '0'; 
-------------------------- end clkgen-----------------
  signal k_globals : klm_globals := klm_globals_null;
--------------------------dut-----------------
  signal dut_ConfigIn_s2m : axiStream_slv32_s2m := axiStream_slv32_s2m_null;
  signal dut_ConfigIn_m2s : axiStream_slv32_m2s := axiStream_slv32_m2s_null;
  signal dut_ConfigOut_s2m : axiStream_slv32_s2m := axiStream_slv32_s2m_null;
  signal dut_ConfigOut_m2s : axiStream_slv32_m2s := axiStream_slv32_m2s_null;
  signal dut_globals : klm_globals := klm_globals_null;
-------------------------- end dut-----------------
--------------------------axprint-----------------
  signal axprint_ConfigIn_s2m : axiStream_slv32_s2m := axiStream_slv32_s2m_null;
  signal axprint_ConfigIn_m2s : axiStream_slv32_m2s := axiStream_slv32_m2s_null;
  signal axprint_globals : klm_globals := klm_globals_null;
-------------------------- end axprint-----------------
  signal data : std_logic_vector(31 downto 0) := x"00000005"; 
-------------------------- end InputDelay_tb-----------------

begin
  -- begin architecture
  
-----------------------------------
proc : process(clkgen_clk) is
  variable mast : axiStream_slv32_master := axiStream_slv32_master_null;
  begin
    if rising_edge(clkgen_clk) then 
      pull( self  =>  mast, tx => dut_ConfigIn_s2m);
  
      if (ready_to_send_0(self => mast)) then 
        send_data_01(self => mast, dataIn => data);
        data <= data + 1;
        
      end if;
        push( self  =>  mast, tx => dut_ConfigIn_m2s);
  end if;
  
  end process;
  -- end architecture
  clkgen : entity work.clk_generator port map (
    clk => clkgen_clk
  );
  
  dut : entity work.InputDelay port map (
    ConfigIn_s2m => dut_ConfigIn_s2m,
    ConfigIn_m2s => dut_ConfigIn_m2s,
    ConfigOut_s2m => dut_ConfigOut_s2m,
    ConfigOut_m2s => dut_ConfigOut_m2s,
    globals => dut_globals
  );
  
  axprint : entity work.InputDelay_print port map (
    ConfigIn_s2m => axprint_ConfigIn_s2m,
    ConfigIn_m2s => axprint_ConfigIn_m2s,
    globals => axprint_globals
  );
  k_globals.clk <= clkgen_clk;
  dut_globals <= k_globals;
  ---------------------------------------------------------------------
--  axprint_ConfigIn << dut_ConfigOut
axprint_ConfigIn_m2s <= dut_ConfigOut_m2s;
dut_ConfigOut_s2m <= axprint_ConfigIn_s2m;
  axprint_globals <= k_globals;
  
end architecture;