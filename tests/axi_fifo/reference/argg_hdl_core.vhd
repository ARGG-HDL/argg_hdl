
-- XGEN: Autogenerated File

library IEEE;
use IEEE.numeric_std.all;
use IEEE.std_logic_1164.all;
use ieee.std_logic_unsigned.all;


package argg_hdl_core is 
    procedure push(self : inout std_logic ; signal data : out std_logic) ;
    procedure pull(self : inout std_logic ; signal data : in std_logic) ;
    procedure push(self : inout std_logic_vector ; signal data : out std_logic_vector) ;
    procedure pull(self : inout std_logic_vector ; signal data  : in std_logic_vector) ;

    function ah_min(lhs : integer; rhs : integer) return integer;

    function std_logic_vector_ctr(data : integer; size_ : integer) return std_logic_vector;
    function to_bool(data : std_logic_vector) return boolean;

    function std_logic_ctr(data : integer; size_ : integer := 1 ) return std_logic;
    function to_bool(data : std_logic) return boolean;

    function unsigned_ctr(data : integer; size_ : integer) return unsigned;
    function to_bool(data :  unsigned) return boolean;

    function   signed_ctr(data : integer; size_ : integer) return   signed;
    function to_bool(data :  signed) return boolean;

    function to_bool(data :  integer) return boolean;

    function to_bool(data :  boolean) return boolean;
    
end argg_hdl_core;


package body argg_hdl_core is
    procedure push(self : inout std_logic ; signal data : out std_logic) is 
    begin 
        data <= self ;
    end procedure;

    procedure pull(self : inout std_logic ; signal data : in std_logic) is 
    begin 
        self := data;
    end procedure;

    procedure push(self : inout std_logic_vector ; signal data : out std_logic_vector) is 
    begin 
        data <= self ;
    end procedure;

    procedure pull(self : inout std_logic_vector ; signal data  : in std_logic_vector) is 
    begin 
        self := data;
    end procedure;
    
    function ah_min(lhs : integer; rhs : integer) return integer is

    begin 

        if (lhs < rhs) then 
            return lhs;
        end if;

        return rhs;

    end function;

    function std_logic_vector_ctr(data : integer; size_ : integer) return std_logic_vector is
        variable ret : std_logic_vector(size_ downto 0) :=( others => '0');
    begin 
        ret := std_logic_vector(to_unsigned(data, ret'length));
        return ret;
    end function;

    function to_bool(data : std_logic_vector) return boolean is 
    begin
        return  (data /= 0);
    end function;

    
    function std_logic_ctr(data : integer; size_ : integer := 1 ) return std_logic is 
        variable ret : std_logic := '0';
    begin
        if data > 0 then
            ret := '1';
        end if;
        return ret;
    end function;
    
    function to_bool(data : std_logic) return boolean is 
    begin
        return  data = '1';
    end function;

    function unsigned_ctr(data : integer; size_ : integer) return unsigned is 
        variable ret : unsigned(size_ downto 0) :=( others => '0');
    begin
        ret := to_unsigned(data, ret'length);
        return ret;
    end function;

    function to_bool(data :  unsigned) return boolean is 
    begin
        return (data /= 0);
    end function;

    function   signed_ctr(data : integer; size_ : integer) return   signed is
        variable ret : signed(size_ downto 0) :=( others => '0');
    begin
        ret :=  to_signed(data, ret'length);
        return ret;
    end function;

    function to_bool(data :  signed) return boolean is 
    begin
        return data /= 0;
    end function;

    function to_bool(data :  integer) return boolean is 
    begin 
        return data /= 0;
    end function;

      function to_bool(data :  boolean) return boolean is 
      begin 
        return data;
      end function;
end argg_hdl_core;
