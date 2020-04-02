
import functools
import argparse
import os,sys,inspect
import copy


from argg_hdl.argg_hdl_base import *
from argg_hdl.argg_hdl_v_symbol import *

from argg_hdl.argg_hdl_simulation import *
from argg_hdl.argg_hdl_v_entity import *


from argg_hdl.examples.axiStream import *
from argg_hdl.examples.axi_stream_delay import *
from argg_hdl.examples.clk_generator import *
from argg_hdl.examples.system_globals import *


class SerialDataConfig(v_class):
    def __init__(self):
        super().__init__("SerialDataConfig")
        self.__v_classType__       = v_classType_t.Record_t

        self.row_Select            =  v_slv(3)
        self.column_select         =  v_slv(6)
        self.ASIC_NUM              =  v_slv(5)
        self.force_test_pattern    =  v_sl() 
        self.sample_start          =  v_slv(5)
        self.sample_stop           =  v_slv(5)




class InputDelay(v_entity):
    def __init__(self,k_globals =None,InputType = v_slv(32),Delay=0):
        super().__init__()
        self.globals  = port_Slave(system_globals())
        if k_globals != None:
            self.globals  << k_globals
        self.ConfigIn = port_Stream_Slave(axisStream( InputType))
        self.ConfigOut = port_Stream_Master(axisStream( InputType))
        self.Delay = Delay
        self.architecture()

    @architecture
    def architecture(self):
        pipe2 = delay(times=self.Delay,obj=self)
        end_architecture()


def delay(times,obj):
    pipe1 = obj.ConfigIn |  stream_delay_one(obj.globals.clk,  obj.ConfigIn.data) 
    for x in range(times):
        pipe1 |   stream_delay_one(obj.globals.clk,  obj.ConfigIn.data) 
            

    pipe1 |   obj.ConfigOut
    return pipe1

class InputDelay_print(v_entity):
    def __init__(self,k_globals =None,InputType =v_slv(32)):
        super().__init__()
        self.globals  = port_Slave(system_globals())
        if k_globals != None:
            self.globals << k_globals
        self.ConfigIn = port_Stream_Slave(axisStream( InputType))
        self.architecture()

    @architecture
    def architecture(self):
        d =  v_copy(self.ConfigIn.data)
        ax_slave = get_salve(self.ConfigIn)
        counter = v_int(0)
        @rising_edge(self.globals.clk)
        def proc():
            counter << counter + 1
            if ax_slave :
               d << ax_slave
               #print("InputDelay_print", value(d))
            
            if counter > 15:
                counter << 0


        end_architecture()

class InputDelay_tb(v_entity):
    def __init__(self):
        super().__init__()
        self.architecture()

    @architecture
    def architecture(self):
        clkgen = v_create(clk_generator())
        k_globals = system_globals()
        data = v_slv(32,5)


        dut  = v_create(InputDelay(k_globals,Delay=5) )

        axprint  =  v_create( InputDelay_print(k_globals))

        axprint.ConfigIn << dut.ConfigOut
        k_globals.clk << clkgen.clk
        mast = get_master(dut.ConfigIn)






        @rising_edge(clkgen.clk)
        def proc():
            if mast:
                mast << data
                data << data + 1
           

        end_architecture()





