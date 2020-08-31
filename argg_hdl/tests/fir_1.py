from enum import Enum, auto
import pandas as pd 
from argg_hdl import *
from  argg_hdl.examples import *

from .helpers import Folders_isSame, vhdl_conversion, do_simulation,printf, printff


def t_data_pipe():
    return v_list(v_signed(8),4)
def t_coeff():
    return v_list(v_signed(8),4)
        
def t_mult():
    return v_list(v_signed(16),4)
        
def t_add_st0():
    return v_list(v_signed(16+1),2)

class fir_basic(v_clk_entity):
    def __init__(self, clk):
        super().__init__(clk)
        self.i_rstb      = port_in(v_sl())
    
        self.i_coeff_0   = port_in(v_slv(8))
        self.i_coeff_1   = port_in(v_slv(8))
        self.i_coeff_2   = port_in(v_slv(8))
        self.i_coeff_3   = port_in(v_slv(8)) 
  
        self.i_data      = port_in(v_slv(8)) 
  
        self.o_data      = port_out(v_slv(8)) 
        self.architecture()

    @architecture
    def architecture(self):

        local_data     = v_signed(8)
        r_coeff        = t_coeff()
        p_data         = t_data_pipe()
        r_mult         = t_mult()
        r_add_st0      = t_add_st0()
        r_add_st1      = v_signed(16+2)
        
        local_data << self.i_data
        @rising_edge(self.clk)
        def p_input():
            if self.i_rstb:
                r_coeff.reset()
            p_data      << (local_data & p_data[0:-1] )
            r_coeff[0]  << self.i_coeff_0
            r_coeff[1]  << self.i_coeff_1
            r_coeff[2]  << self.i_coeff_2
            r_coeff[3]  << self.i_coeff_3

            
        @rising_edge(self.clk)
        def p_mult():
            if self.i_rstb:
                r_mult.reset()

            for index in range(len(r_mult)):
                r_mult[index] << p_data[index] * r_coeff[index]
            
        @rising_edge(self.clk)
        def p_add_st0():
            if self.i_rstb:
                r_add_st0.reset()

            for index in range(2):
                r_add_st0[index] << resize(r_mult[2*index] ,16+1) +resize( r_mult[2*index+1],16+1)

        @rising_edge(self.clk)
        def p_add_st1():
            if self.i_rstb:
                r_add_st1.reset()
            r_add_st1 << resize(r_add_st0[0],16+2) +resize(r_add_st0[1],16+2)

        @rising_edge(self.clk)
        def p_output():
            if self.i_rstb:
                self.o_data.reset()
            self.o_data  << r_add_st1[8:]

        end_architecture()

import math
class fir_basic_tb(v_entity):
    def __init__(self ):
        super().__init__()
        self.architecture()



    @architecture
    def architecture(self):
        clk = clk_generator()
        fir1 = fir_basic(clk.clk)
        fir1.i_coeff_0   << 60
        fir1.i_coeff_1   << -60
        fir1.i_coeff_2   << 60
        fir1.i_coeff_3   << -60
        cnt = v_slv(16) 

        @rising_edge(clk.clk)
        def proc():
            cnt << cnt +1

            fir1.i_data <<  int(math.sin( value(cnt) /10) *100)
            
            printf( str(value(fir1.i_data)) + "; " + str(value(fir1.o_data)) + "\n")
        
        end_architecture()

@do_simulation
def fir_basic_tb_sim(OutputPath, f= None):
    tb = fir_basic_tb()
    return tb

@vhdl_conversion
def  fir_basic_tb2vhdl(OutputPath):
    gSystem = system_globals()
    tb1 =  fir_basic( v_sl())
    return tb1
