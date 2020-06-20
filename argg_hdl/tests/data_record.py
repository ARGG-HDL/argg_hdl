from enum import Enum, auto
import pandas as pd 
from argg_hdl import *
from  argg_hdl.examples import *

from .helpers import Folders_isSame, vhdl_conversion, do_simulation,printf, printff


def sr_clk_t(val=0):
    return v_slv(8,val)


class span_t(v_data_record):
    def __init__(self, start  , stop ):
        super().__init__()
        self.start  = sr_clk_t(start)
        self.stop   = sr_clk_t(stop)
    
    def isInRange(self,counter):
        return self.start <= counter and counter <= self.stop

    def isBeforeRange(self, counter):
        return counter < self.start

    def isAfterRange(self, counter):
        return self.stop < counter 



class span_t2(v_record):
    def __init__(self, start  , stop ):
        super().__init__()
        self.start  = sr_clk_t(start)
        self.stop   = sr_clk_t(stop)
    
    def isInRange(self,counter):
        return self.start <= counter and counter <= self.stop

    def isBeforeRange(self, counter):
        return counter < self.start

    def isAfterRange(self, counter):
        return self.stop < counter 


class test_Config(v_record):
    def __init__(self):
        super().__init__()
        self.var1             = span_t(1,0x10)
        self.var2             = v_dataObject(span_t(2,0x20))
        self.var3             = span_t2(3,0x30)
        self.var4             = v_dataObject(span_t2(4,0x40))
        self.var5             = sr_clk_t(5)
        self.var6             = v_dataObject(sr_clk_t(6))


class data_record_tb(v_entity):
    

    def __init__(self):
        super().__init__()
        self.architecture()

    @architecture
    def architecture(self):
        clkgen     = clk_generator()
        config1    = v_signal(test_Config())
        config2    = v_variable(test_Config())
        counter    = sr_clk_t(0)
        in_range    = v_sl()
        befor_range    = v_sl()
        after_range    = v_sl()
        anotherSpan = v_signal(span_t(12, 45))

        @rising_edge(clkgen.clk)
        def proc():
            in_range << 0
            befor_range << 0
            after_range << 0
            counter << counter + 1
            config1.var1 << config2.var1
            config2.var2 << config1.var2

            if config1.var3.isInRange(counter):
                printf("config1.var3.isInRange(counter): "+ str(value(counter)) + "\n" )
                in_range << 1

            if config1.var4.isBeforeRange(counter):
                printf("config1.var4.isBeforeRange(counter): "+ str(value(counter)) + "\n")
                befor_range << 1

            if config1.var4.isAfterRange(counter):
                printf("config1.var4.isAfterRange(counter): "+ str(value(counter)) + "\n")
                after_range << 1

            if anotherSpan.isInRange(counter):
                printf("anotherSpan.isInRange(counter): "+ str(value(counter)) + "\n")


        end_architecture()


@do_simulation
def data_record_tb_sim(OutputPath, f= None):
    
    tb1 = data_record_tb()
    return tb1

@vhdl_conversion
def data_record_tb_2vhdl(OutputPath, f= None):
    
    tb1 = data_record_tb()
    return tb1