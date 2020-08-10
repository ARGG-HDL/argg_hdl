import argg_hdl.tests.ex1 as ex1
import argg_hdl.tests.ex3 as ex3
import argg_hdl.tests.test_axi_fifo as test_axi_fifo
from argg_hdl.tests.helpers  import remove_old_files
import argg_hdl.tests.Native_fifo as Native_fifo

import argg_hdl.tests.EnumTest as EnumTest
import argg_hdl.tests.slice_testing as slice_testing
import argg_hdl.tests.TargetX_readout as TX

from argg_hdl.argg_hdl_base import  hdl_constructor

import argg_hdl.tests.TargetX_readout   as TX
import argg_hdl.tests.data_record as dr 

import  argg_hdl.tests.fir_1 as fir_1

remove_old_files()



#result, message = ex1.InputDelay_sim("tests/ex1/")
#result, message = ex3.ex32vhdl("tests/ex3/")


#dr.data_record_tb_sim("tests/data_record_tb_sim/")
#dr.data_record_tb_2vhdl("tests/data_record_tb/")

#TX.TXReadout2vhdl("../vhdl_lecture/targetx")

#TX.TX_sampling_controller_sim("tests/targetx_sim2",20000)
#TX.TX_write_handler_tb_sim("tests/targetx_sim3",20000)
#TX.TX_write_handler2vhdl("../vhdl_lecture/targetx2")

#fir_1.fir_basic_tb_sim("tests/fir_1_sim",20000)
fir_1.fir_basic_tb2vhdl("../vhdl_lecture/fir_1")

#TX.TXReadout_sim("tests/targetx_sim",20000)
#test_axi_fifo.test_bench_axi_fifo_sim("tests/axi_fifo_sim")
#Signal_Variable_class.var_sig_tb_2vhdl("tests/var_sig_class")
#Signal_Variable_class.var_sig_tb_sim("tests/var_sig_class_sim")
#Native_fifo.fifo_cc_tb_sim("tests/native_fifo_sim")

#slice_testing.slice_TB_sim("tests/slice_TB_sim")
#slice_testing.slice_TB_2vhdl("tests/slice_TB")
#EnumTest.enum_TB_2vhdl("tests/enumTest")