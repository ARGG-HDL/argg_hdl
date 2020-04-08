
import functools
import argparse
import os,sys,inspect
import copy


from argg_hdl import *

import argg_hdl.examples as  ahe
import argg_hdl.argg_hdl_debug_vis as debug_vis

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


class register_t(v_class):
    def __init__(self):
        super().__init__("register_t")
        self.__v_classType__       = v_classType_t.Record_t
        self.address   = v_slv(16) 
        self.value     = v_slv(16) 
        


class klm_globals(v_class):
    def __init__(self):
        super().__init__("klm_globals")
        self.__v_classType__       = v_classType_t.Record_t
        self.clk   =  v_sl() 
        self.rst   =  v_sl() 
        self.reg   =  register_t() 

class InputDelay(v_entity):
    def __init__(self,k_globals =None,InputType = v_slv(32),Delay=0):
        super().__init__()
        self.globals  = port_Slave(klm_globals())
        if k_globals != None:
            self.globals  << k_globals
        self.ConfigIn = port_Stream_Slave(ahe.axisStream( InputType))
        self.ConfigOut = port_Stream_Master(ahe.axisStream( InputType))
        self.Delay = Delay
        self.architecture()

    @architecture
    def architecture(self):
        
#        pipe = self.ConfigIn \
#            | stream_delay_one(self.globals.clk, self.ConfigIn.data,0) \
#            | stream_delay_one(self.globals.clk, self.ConfigIn.data,1) \
#            | \
#        self.ConfigOut   
        pipe2 = delay(times=self.Delay,obj=self)
        end_architecture()


def delay(times,obj):
    pipe1 = obj.ConfigIn |  ahe.stream_delay_one(obj.globals.clk,  obj.ConfigIn.data) 
    for _ in range(times):
        pipe1 |   ahe.stream_delay_one(obj.globals.clk,  obj.ConfigIn.data) 
            

    pipe1 |   obj.ConfigOut
    return pipe1

class InputDelay_print(v_entity):
    def __init__(self,k_globals =None,InputType =v_slv(32)):
        super().__init__()
        self.globals  = port_Slave(klm_globals())
        if k_globals != None:
            self.globals << k_globals
        self.ConfigIn = port_Stream_Slave(ahe.axisStream( InputType))
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
               ax_slave >> d  
               #print("InputDelay_print", value(d))
            
            if counter > 15:
                counter << 0


        end_architecture()

class dataSource(v_entity):
    def __init__(self,clk,outputType =v_slv(32)):
        super().__init__()
        self.clk = port_in(v_sl())

        self.DataOut = port_Stream_Master(ahe.axisStream( outputType))
        self.architecture()

    @architecture
    def architecture(self):
        mast = get_handle(self.DataOut)
        data = v_slv(32,5)

        @rising_edge(self.clk)
        def proc():
            if mast:
                mast << data
                data << data + 2
           

class InputDelay_tb(v_entity):
    def __init__(self):
        super().__init__()
        self.architecture()

    @architecture
    def architecture(self):
        clkgen = v_create(ahe.clk_generator())
        k_globals =klm_globals()
        data = v_slv(32,5)


        dut  = v_create(InputDelay(k_globals,Delay=5) )

        axprint  =  v_create( InputDelay_print(k_globals))

        axprint.ConfigIn << dut.ConfigOut
        k_globals.clk << clkgen.clk

        d_source  =  v_create( dataSource(k_globals.clk))
        dut.ConfigIn << d_source.DataOut




        end_architecture()




def main():

    tb  =v_create(InputDelay_tb())
    #run_simulation(tb, 3000,"InputDelay_tb.vcd")
    convert_to_hdl(tb, "InputDelay_tb")

main()