import argg_hdl.examples.axiStream as ax
import argg_hdl.examples.clk_generator as clk_gen 
import  argg_hdl.examples.counter   as cntr
import argg_hdl.examples.edgeDetection  as e_detection
import argg_hdl.examples.inputDelayTest  as iDelay
import argg_hdl.examples.ram_handle  as ram_h
import argg_hdl.examples.rollingCounter as r_counter
import argg_hdl.examples.system_globals  as sys_globals
import argg_hdl.examples.axi_stream_delay  as ax_s_delay


## argg_hdl.examples.axiStream
axisStream = ax.axisStream
axisStream_slave = ax.axisStream_slave
axisStream_master = ax.axisStream_master


## argg_hdl.examples.clk_generator
clk_generator  = clk_gen.clk_generator

## argg_hdl.examples.counter
time_span   = cntr.time_span
counter     = cntr.counter

## edgeDetection
edgeDetection  = e_detection.edgeDetection

## inputDelayTest
InputDelay_tb = iDelay.InputDelay_tb

## ram_handle
ram_handle = ram_h.ram_handle
ram_handle_master = ram_h.ram_handle_master

##  rollingCounter
rollingCounter = r_counter.rollingCounter


## system_globals
system_globals = sys_globals.system_globals


stream_delay = ax_s_delay.stream_delay
stream_delay_one = ax_s_delay.stream_delay_one