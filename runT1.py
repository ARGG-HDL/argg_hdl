import argg_hdl.tests.ex1 as ex1
import argg_hdl.tests.ex3 as ex3
import argg_hdl.tests.test_axi_fifo as test_axi_fifo
from argg_hdl.tests.helpers  import remove_old_files
import argg_hdl.tests.Native_fifo as Native_fifo

import argg_hdl.tests.EnumTest as EnumTest
import argg_hdl.tests.slice_testing as slice_testing
import argg_hdl.tests.TargetX_readout as TX
remove_old_files()




#result, message = ex1.InputDelay_sim("tests/ex1/")
#result, message = ex3.ex32vhdl("tests/ex3/")

TX.TXReadout2vhdl("../vhdl_lecture/targetx")
#test_axi_fifo.test_bench_axi_fifo_sim("tests/axi_fifo_sim")
#Signal_Variable_class.var_sig_tb_2vhdl("tests/var_sig_class")
#Signal_Variable_class.var_sig_tb_sim("tests/var_sig_class_sim")
#Native_fifo.fifo_cc_tb_sim("tests/native_fifo_sim")

#slice_testing.slice_TB_sim("tests/slice_TB_sim")
#slice_testing.slice_TB_2vhdl("tests/slice_TB")
#EnumTest.enum_TB_2vhdl("tests/enumTest")