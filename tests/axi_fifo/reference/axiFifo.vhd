-- XGEN: Autogenerated File

library IEEE;
library work;
use IEEE.numeric_std.all;
use IEEE.std_logic_1164.all;
use ieee.std_logic_unsigned.all;
use work.argg_hdl_core.all;
use work.axisStream_slv32.all;
use work.slv32_a_pack.all;
use work.v_symbol_pack.all;


entity axiFifo is 
  port(
    Axi_in_s2m :  out  axiStream_slv32_s2m := axiStream_slv32_s2m_ctr;
    Axi_in_m2s :  in  axiStream_slv32_m2s := axiStream_slv32_m2s_ctr;
    Axi_out_s2m :  in  axiStream_slv32_s2m := axiStream_slv32_s2m_ctr;
    Axi_out_m2s :  out  axiStream_slv32_m2s := axiStream_slv32_m2s_ctr;
    clk :  in  std_logic := std_logic_ctr(0, 1)
  );
end entity;



architecture rtl of axiFifo is

--------------------------axiFifo-----------------
  constant array_size : integer := integer_ctr(1024, 32); 
  constant depth : integer := integer_ctr(10, 32); 
  signal head_index : slv11 := std_logic_vector_ctr(0, 11); 
  signal sList : slv32_a(0 to array_size - 1)  := (others => (others => '0'));
  signal tail_index : slv11 := std_logic_vector_ctr(0, 11); 
-------------------------- end axiFifo-----------------

begin
  -- begin p2
    Axi_out_m2s.data <= sList(to_integer(signed( tail_index)));
    -- end p2;
  
  -----------------------------------
  proc : process(clk) is
      variable   axiSalve : axiStream_slv32_slave := axiStream_slv32_slave_ctr;
    variable counter : std_logic_vector(10 downto 0) := (others => '0');
    variable axiSalve_buff : std_logic_vector(31 downto 0) := (others => '0');
    variable i_valid : std_logic := '0';
    begin
      if rising_edge(clk) then 
        pull( self  =>  axiSalve, rx => Axi_in_m2s);
    
        if (( isReceivingData_0(self => axiSalve) and counter < sList'length) ) then 
          read_data_00(self => axiSalve, dataOut => axiSalve_buff);
          sList(to_integer(signed( head_index))) <= axiSalve_buff;
          head_index <= head_index + 1;
          counter := counter + 1;
          
        end if;
      
        if (head_index = sList'length - 1) then 
          head_index <=  (others => '0');
          
        end if;
      
        if (( to_bool(Axi_out_s2m.ready)  and to_bool(i_valid) ) ) then 
          i_valid := '0';
          tail_index <= tail_index + 1;
          counter := counter - 1;
          
        end if;
      
        if ((  not  ( to_bool(i_valid)  )  and counter > 0) ) then 
          i_valid := '1';
          
        end if;
      
        if (tail_index = sList'length - 1) then 
          tail_index <=  (others => '0');
          
        end if;
      Axi_out_m2s.valid <= i_valid;
          push( self  =>  axiSalve, rx => Axi_in_s2m);
    end if;
    
    end process;
  
end architecture;