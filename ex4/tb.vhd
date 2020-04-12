-- XGEN: Autogenerated File

library IEEE;
library UNISIM;
library work;
use IEEE.numeric_std.all;
use IEEE.std_logic_1164.all;
use UNISIM.VComponents.all;
use ieee.std_logic_unsigned.all;
use work.argg_hdl_core.all;
use work.axisStream_slv32.all;
use work.memo_pack.all;
use work.slv32_a_pack.all;


entity tb is 
end entity;



architecture rtl of tb is

--------------------------tb-----------------
--------------------------clkgen-----------------
  signal clkgen_clk : std_logic := '0'; 
-------------------------- end clkgen-----------------
--------------------------axmux-----------------
  signal axmux_clk : std_logic := '0'; 
  signal axmux_data_in_m2s : axiStream_slv32_s2m_a(4 - 1 downto 0)  := (others => axiStream_slv32_s2m_null);
  signal axmux_data_in_s2m : axiStream_slv32_m2s_a(4 - 1 downto 0)  := (others => axiStream_slv32_m2s_null);
  signal axmux_data_out_s2m : axiStream_slv32_s2m := axiStream_slv32_s2m_null;
  signal axmux_data_out_m2s : axiStream_slv32_m2s := axiStream_slv32_m2s_null;
-------------------------- end axmux-----------------
--------------------------d_s-----------------
  signal d_s_clk : std_logic := '0'; 
  signal d_s_data_out_s2m : axiStream_slv32_s2m := axiStream_slv32_s2m_null;
  signal d_s_data_out_m2s : axiStream_slv32_m2s := axiStream_slv32_m2s_null;
-------------------------- end d_s-----------------
  signal m_sig : memo_sig := memo_sig_null;
  signal d : std_logic_vector(31 downto 0) := (others => '0'); 
  signal d2 : std_logic_vector(31 downto 0) := (others => '0'); 
-------------------------- end tb-----------------

begin
  -- begin architecture
  
-----------------------------------
proc : process(clkgen_clk) is
  begin
    if rising_edge(clkgen_clk) then 
  set_data_01(self_sig => m_sig, data => d);
    get_data_01(self_sig => m_sig, data => d2);
    end if;
  
  end process;
  -- end architecture

  clkgen : entity work.clk_generator port map (
    clk => clkgen_clk
  );
  
  axmux : entity work.axiStreamMux port map (
    clk => axmux_clk,
    data_in_s2m => axmux_data_in_s2m,
    data_in_m2s => axmux_data_in_m2s,
    data_out_s2m => axmux_data_out_s2m,
    data_out_m2s => axmux_data_out_m2s
  );
  
  d_s : entity work.d_source port map (
    clk => d_s_clk,
    data_out_s2m => d_s_data_out_s2m,
    data_out_m2s => d_s_data_out_m2s
  );
  axmux_clk <= clkgen_clk;
  ---------------------------------------------------------------------
--  axmux_data_in(0) << d_s_data_out
axmux_data_in_m2s(0) <= d_s_data_out_m2s;
d_s_data_out_s2m <= axmux_data_in_s2m(0);
  d_s_clk <= clkgen_clk;
  m_sig.l(0) <= d;
  d2 <= m_sig.l(0);
  
end architecture;