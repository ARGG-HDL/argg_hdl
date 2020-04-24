-- XGEN: Autogenerated File

library IEEE;
library UNISIM;
library work;
use IEEE.numeric_std.all;
use IEEE.std_logic_1164.all;
use UNISIM.VComponents.all;
use ieee.std_logic_unsigned.all;
use work.argg_hdl_core.all;


package NativeFifoOut_pack is 

-------------------------------------------------------------------------
------- Start Psuedo Class NativeFifoOut -------------------------

type NativeFifoOut_s2m is record 
    enable : std_logic;
end record;
    
    
  constant NativeFifoOut_s2m_null : NativeFifoOut_s2m:= (
    enable => '0'
  );


    type NativeFifoOut_s2m_a is array (natural range <>) of NativeFifoOut_s2m;
        


type NativeFifoOut_m2s is record 
    data : std_logic_vector(31 downto 0);
    empty : std_logic;
end record;
    
    
  constant NativeFifoOut_m2s_null : NativeFifoOut_m2s:= (
    data => (others => '0'),
    empty => '0'
  );


    type NativeFifoOut_m2s_a is array (natural range <>) of NativeFifoOut_m2s;
        


type NativeFifoOut is record 
    data : std_logic_vector(31 downto 0);
    empty : std_logic;
    enable : std_logic;
end record;
    
    
  constant NativeFifoOut_null : NativeFifoOut:= (
    data => (others => '0'),
    empty => '0',
    enable => '0'
  );


    type NativeFifoOut_a is array (natural range <>) of NativeFifoOut;
        

  procedure pull (self :  inout NativeFifoOut; signal IO_data :  in NativeFifoOut_s2m);
  procedure push (self :  inout NativeFifoOut; signal IO_data :  out NativeFifoOut_m2s);
  procedure pull (self :  inout NativeFifoOut; signal IO_data :  in NativeFifoOut_m2s);
  procedure push (self :  inout NativeFifoOut; signal IO_data :  out NativeFifoOut_s2m);
------- End Psuedo Class NativeFifoOut -------------------------
-------------------------------------------------------------------------


end NativeFifoOut_pack;


package body NativeFifoOut_pack is

-------------------------------------------------------------------------
------- Start Psuedo Class NativeFifoOut -------------------------
procedure pull (self :  inout NativeFifoOut; signal IO_data :  in NativeFifoOut_s2m) is
   
  begin 
 
    
-- Start Connecting
    pull(self.enable, IO_data.enable);

-- End Connecting
    
             
end procedure;

procedure push (self :  inout NativeFifoOut; signal IO_data :  out NativeFifoOut_m2s) is
   
  begin 
 
    
-- Start Connecting
    push(self.data, IO_data.data);
    push(self.empty, IO_data.empty);

-- End Connecting
    
             
end procedure;

procedure pull (self :  inout NativeFifoOut; signal IO_data :  in NativeFifoOut_m2s) is
   
  begin 
 
    
-- Start Connecting
    pull(self.data, IO_data.data);
    pull(self.empty, IO_data.empty);

-- End Connecting
    
             
end procedure;

procedure push (self :  inout NativeFifoOut; signal IO_data :  out NativeFifoOut_s2m) is
   
  begin 
 
    
-- Start Connecting
    push(self.enable, IO_data.enable);

-- End Connecting
    
             
end procedure;

------- End Psuedo Class NativeFifoOut -------------------------
  -------------------------------------------------------------------------


end NativeFifoOut_pack;

