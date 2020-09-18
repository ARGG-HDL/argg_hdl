-- XGEN: Autogenerated File

library IEEE;
library work;
use IEEE.numeric_std.all;
use IEEE.std_logic_1164.all;
use ieee.std_logic_unsigned.all;
use work.argg_hdl_core.all;
use work.axisStream_slv32.all;
use work.klm_globals_pack.all;
use work.register_t_pack.all;
use work.v_symbol_pack.all;


entity InputDelay is 
  port(
    ConfigIn_s2m :  out  axiStream_slv32_s2m := axiStream_slv32_s2m_ctr;
    ConfigIn_m2s :  in  axiStream_slv32_m2s := axiStream_slv32_m2s_ctr;
    ConfigOut_s2m :  in  axiStream_slv32_s2m := axiStream_slv32_s2m_ctr;
    ConfigOut_m2s :  out  axiStream_slv32_m2s := axiStream_slv32_m2s_ctr;
    globals :  in  klm_globals := klm_globals_ctr;
    globals_clk :  in  std_logic := std_logic_ctr(0, 1)
  );
end entity;



architecture rtl of InputDelay is

--------------------------InputDelay-----------------
--------------------------pipe2-----------------
--------------------------pipe2_2_stream_delay_one-----------------
  signal   pipe2_2_stream_delay_one_Axi_in_s2m : axiStream_slv32_s2m := axiStream_slv32_s2m_ctr;
  signal   pipe2_2_stream_delay_one_Axi_in_m2s : axiStream_slv32_m2s := axiStream_slv32_m2s_ctr;
  signal   pipe2_2_stream_delay_one_Axi_out_s2m : axiStream_slv32_s2m := axiStream_slv32_s2m_ctr;
  signal   pipe2_2_stream_delay_one_Axi_out_m2s : axiStream_slv32_m2s := axiStream_slv32_m2s_ctr;
-------------------------- end pipe2_2_stream_delay_one-----------------
--------------------------pipe2_3_stream_delay_one-----------------
  signal   pipe2_3_stream_delay_one_Axi_in_s2m : axiStream_slv32_s2m := axiStream_slv32_s2m_ctr;
  signal   pipe2_3_stream_delay_one_Axi_in_m2s : axiStream_slv32_m2s := axiStream_slv32_m2s_ctr;
  signal   pipe2_3_stream_delay_one_Axi_out_s2m : axiStream_slv32_s2m := axiStream_slv32_s2m_ctr;
  signal   pipe2_3_stream_delay_one_Axi_out_m2s : axiStream_slv32_m2s := axiStream_slv32_m2s_ctr;
-------------------------- end pipe2_3_stream_delay_one-----------------
--------------------------pipe2_4_stream_delay_one-----------------
  signal   pipe2_4_stream_delay_one_Axi_in_s2m : axiStream_slv32_s2m := axiStream_slv32_s2m_ctr;
  signal   pipe2_4_stream_delay_one_Axi_in_m2s : axiStream_slv32_m2s := axiStream_slv32_m2s_ctr;
  signal   pipe2_4_stream_delay_one_Axi_out_s2m : axiStream_slv32_s2m := axiStream_slv32_s2m_ctr;
  signal   pipe2_4_stream_delay_one_Axi_out_m2s : axiStream_slv32_m2s := axiStream_slv32_m2s_ctr;
-------------------------- end pipe2_4_stream_delay_one-----------------
--------------------------pipe2_5_stream_delay_one-----------------
  signal   pipe2_5_stream_delay_one_Axi_in_s2m : axiStream_slv32_s2m := axiStream_slv32_s2m_ctr;
  signal   pipe2_5_stream_delay_one_Axi_in_m2s : axiStream_slv32_m2s := axiStream_slv32_m2s_ctr;
  signal   pipe2_5_stream_delay_one_Axi_out_s2m : axiStream_slv32_s2m := axiStream_slv32_s2m_ctr;
  signal   pipe2_5_stream_delay_one_Axi_out_m2s : axiStream_slv32_m2s := axiStream_slv32_m2s_ctr;
-------------------------- end pipe2_5_stream_delay_one-----------------
--------------------------pipe2_6_stream_delay_one-----------------
  signal   pipe2_6_stream_delay_one_Axi_in_s2m : axiStream_slv32_s2m := axiStream_slv32_s2m_ctr;
  signal   pipe2_6_stream_delay_one_Axi_in_m2s : axiStream_slv32_m2s := axiStream_slv32_m2s_ctr;
  signal   pipe2_6_stream_delay_one_Axi_out_s2m : axiStream_slv32_s2m := axiStream_slv32_s2m_ctr;
  signal   pipe2_6_stream_delay_one_Axi_out_m2s : axiStream_slv32_m2s := axiStream_slv32_m2s_ctr;
-------------------------- end pipe2_6_stream_delay_one-----------------
--------------------------pipe2_7_stream_delay_one-----------------
  signal   pipe2_7_stream_delay_one_Axi_in_s2m : axiStream_slv32_s2m := axiStream_slv32_s2m_ctr;
  signal   pipe2_7_stream_delay_one_Axi_in_m2s : axiStream_slv32_m2s := axiStream_slv32_m2s_ctr;
  signal   pipe2_7_stream_delay_one_Axi_out_s2m : axiStream_slv32_s2m := axiStream_slv32_s2m_ctr;
  signal   pipe2_7_stream_delay_one_Axi_out_m2s : axiStream_slv32_m2s := axiStream_slv32_m2s_ctr;
-------------------------- end pipe2_7_stream_delay_one-----------------
-------------------------- end pipe2-----------------
-------------------------- end InputDelay-----------------

begin
  -- begin architecture
  -- end architecture

  pipe2_2_stream_delay_one : entity work.stream_delay_one port map (
    Axi_in_s2m => pipe2_2_stream_delay_one_Axi_in_s2m,
    Axi_in_m2s => pipe2_2_stream_delay_one_Axi_in_m2s,
    Axi_out_s2m => pipe2_2_stream_delay_one_Axi_out_s2m,
    Axi_out_m2s => pipe2_2_stream_delay_one_Axi_out_m2s,
    clk => globals_clk
  );
  pipe2_3_stream_delay_one : entity work.stream_delay_one port map (
    Axi_in_s2m => pipe2_3_stream_delay_one_Axi_in_s2m,
    Axi_in_m2s => pipe2_3_stream_delay_one_Axi_in_m2s,
    Axi_out_s2m => pipe2_3_stream_delay_one_Axi_out_s2m,
    Axi_out_m2s => pipe2_3_stream_delay_one_Axi_out_m2s,
    clk => globals_clk
  );
  pipe2_4_stream_delay_one : entity work.stream_delay_one port map (
    Axi_in_s2m => pipe2_4_stream_delay_one_Axi_in_s2m,
    Axi_in_m2s => pipe2_4_stream_delay_one_Axi_in_m2s,
    Axi_out_s2m => pipe2_4_stream_delay_one_Axi_out_s2m,
    Axi_out_m2s => pipe2_4_stream_delay_one_Axi_out_m2s,
    clk => globals_clk
  );
  pipe2_5_stream_delay_one : entity work.stream_delay_one port map (
    Axi_in_s2m => pipe2_5_stream_delay_one_Axi_in_s2m,
    Axi_in_m2s => pipe2_5_stream_delay_one_Axi_in_m2s,
    Axi_out_s2m => pipe2_5_stream_delay_one_Axi_out_s2m,
    Axi_out_m2s => pipe2_5_stream_delay_one_Axi_out_m2s,
    clk => globals_clk
  );
  pipe2_6_stream_delay_one : entity work.stream_delay_one port map (
    Axi_in_s2m => pipe2_6_stream_delay_one_Axi_in_s2m,
    Axi_in_m2s => pipe2_6_stream_delay_one_Axi_in_m2s,
    Axi_out_s2m => pipe2_6_stream_delay_one_Axi_out_s2m,
    Axi_out_m2s => pipe2_6_stream_delay_one_Axi_out_m2s,
    clk => globals_clk
  );
  pipe2_7_stream_delay_one : entity work.stream_delay_one port map (
    Axi_in_s2m => pipe2_7_stream_delay_one_Axi_in_s2m,
    Axi_in_m2s => pipe2_7_stream_delay_one_Axi_in_m2s,
    Axi_out_s2m => pipe2_7_stream_delay_one_Axi_out_s2m,
    Axi_out_m2s => pipe2_7_stream_delay_one_Axi_out_m2s,
    clk => globals_clk
  );
  ---------------------------------------------------------------------
--  ConfigOut << pipe2_7_stream_delay_one_Axi_out
ConfigOut_m2s <= pipe2_7_stream_delay_one_Axi_out_m2s;
pipe2_7_stream_delay_one_Axi_out_s2m <= ConfigOut_s2m;
  ---------------------------------------------------------------------
--  pipe2_2_stream_delay_one_Axi_in << ConfigIn
pipe2_2_stream_delay_one_Axi_in_m2s <= ConfigIn_m2s;
ConfigIn_s2m <= pipe2_2_stream_delay_one_Axi_in_s2m;
  ---------------------------------------------------------------------
--  pipe2_3_stream_delay_one_Axi_in << pipe2_2_stream_delay_one_Axi_out
pipe2_3_stream_delay_one_Axi_in_m2s <= pipe2_2_stream_delay_one_Axi_out_m2s;
pipe2_2_stream_delay_one_Axi_out_s2m <= pipe2_3_stream_delay_one_Axi_in_s2m;
  ---------------------------------------------------------------------
--  pipe2_4_stream_delay_one_Axi_in << pipe2_3_stream_delay_one_Axi_out
pipe2_4_stream_delay_one_Axi_in_m2s <= pipe2_3_stream_delay_one_Axi_out_m2s;
pipe2_3_stream_delay_one_Axi_out_s2m <= pipe2_4_stream_delay_one_Axi_in_s2m;
  ---------------------------------------------------------------------
--  pipe2_5_stream_delay_one_Axi_in << pipe2_4_stream_delay_one_Axi_out
pipe2_5_stream_delay_one_Axi_in_m2s <= pipe2_4_stream_delay_one_Axi_out_m2s;
pipe2_4_stream_delay_one_Axi_out_s2m <= pipe2_5_stream_delay_one_Axi_in_s2m;
  ---------------------------------------------------------------------
--  pipe2_6_stream_delay_one_Axi_in << pipe2_5_stream_delay_one_Axi_out
pipe2_6_stream_delay_one_Axi_in_m2s <= pipe2_5_stream_delay_one_Axi_out_m2s;
pipe2_5_stream_delay_one_Axi_out_s2m <= pipe2_6_stream_delay_one_Axi_in_s2m;
  ---------------------------------------------------------------------
--  pipe2_7_stream_delay_one_Axi_in << pipe2_6_stream_delay_one_Axi_out
pipe2_7_stream_delay_one_Axi_in_m2s <= pipe2_6_stream_delay_one_Axi_out_m2s;
pipe2_6_stream_delay_one_Axi_out_s2m <= pipe2_7_stream_delay_one_Axi_in_s2m;
  
end architecture;