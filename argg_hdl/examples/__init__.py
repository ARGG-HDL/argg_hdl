from argg_hdl.examples import axiStream as ax
#import argg_hdl.examples.axiStream as ax
from argg_hdl.examples import clk_generator as clk_gen 
from argg_hdl.examples import counter   as cntr
from argg_hdl.examples import edgeDetection  as e_detection
from argg_hdl.examples import inputDelayTest  as iDelay
from argg_hdl.examples import ram_handle  as ram_h
from argg_hdl.examples import rollingCounter as r_counter
from argg_hdl.examples import system_globals  as sys_globals
from argg_hdl.examples import axi_stream_delay  as ax_s_delay
from argg_hdl.examples import optional_t as opt_t
from argg_hdl.examples import small_buffer as sb

from argg_hdl.examples import axi_fifo as ax_fifo

from argg_hdl.examples import axiPrint as axiPrint

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
system_globals        = sys_globals.system_globals
register_t            = sys_globals.register_t
system_globals_delay  = sys_globals.system_globals_delay

stream_delay = ax_s_delay.stream_delay
stream_delay_one = ax_s_delay.stream_delay_one


#optional_t
optional_t = opt_t.optional_t


small_buffer = sb.small_buffer

axiFifo = ax_fifo.axiFifo

axiPrint = axiPrint.axiPrint