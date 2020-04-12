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


entity axiStreamMux is 
  port(
    clk :  in  std_logic := '0';
    data_in_s2m :  out  axiStream_slv32_s2m_a(4 downto 0) := (others => axiStream_slv32_s2m_null);
    data_in_m2s :  in  axiStream_slv32_m2s_a(4 downto 0) := (others => axiStream_slv32_m2s_null);
    data_out_s2m :  in  axiStream_slv32_s2m := axiStream_slv32_s2m_null;
    data_out_m2s :  out  axiStream_slv32_m2s := axiStream_slv32_m2s_null
  );
end entity;



architecture rtl of axiStreamMux is

--------------------------axiStreamMux-----------------
  signal data_buffer : std_logic_vector(31 downto 0) := (others => '0'); 
  signal ChannelUsed : integer := 0; 
  signal sending : std_logic := '0'; 
-------------------------- end axiStreamMux-----------------

begin
  -- begin architecture
  
-----------------------------------
proc : process(clk) is
    variable d_in : axiStream_slv32_slave_a(4 - 1 downto 0)  := (others => axiStream_slv32_slave_null);
  variable d_out : axiStream_slv32_master := axiStream_slv32_master_null;
  begin
    if rising_edge(clk) then 
    pull(d_in, data_in_m2s);
        pull( self  =>  d_out, tx => data_out_s2m);
  
    if ( not  ( sending = '1' ) ) then 
    for i3 in 0 to d_in'length -1 loop 
      
      if (i3 = ChannelUsed) then 
        ChannelUsed <= d_in'length + 1;
        next;
        
      end if;
      
      if (( isReceivingData_0(self => d_in(i3)) and ready_to_send_0(self => d_out)) ) then 
        ChannelUsed <= i3;
        get_value_01_rshift(self => d_in(i3), rhs => data_buffer);
        Send_end_Of_Stream_00(self => d_out, EndOfStream => IsEndOfStream_0(self => d_in(i3)));
        
        if ( not  ( IsEndOfStream_0(self => d_in(i3)) ) ) then 
          sending <= '1';
          
        end if;
        exit;
        
      end if;
    end loop;
    
    elsif (( sending = '1' and isReceivingData_0(self => d_in(ChannelUsed)) and ready_to_send_0(self => d_out)) ) then 
    get_value_00_rshift(self => d_in(ChannelUsed), rhs => d_out);
    Send_end_Of_Stream_00(self => d_out, EndOfStream => IsEndOfStream_0(self => d_in(ChannelUsed)));
    
    if (IsEndOfStream_0(self => d_in(ChannelUsed))) then 
      sending <= '0';
      
    end if;
    
    end if;
      push(d_in, data_in_s2m);
        push( self  =>  d_out, tx => data_out_m2s);
  end if;
  
  end process;
  -- end architecture

end architecture;