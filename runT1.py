import argg_hdl.tests.test_axi_fifo as test_axi_fifo
from argg_hdl.tests.helpers  import remove_old_files
import argg_hdl.tests.Signal_Variable_class as Signal_Variable_class

remove_old_files()


#test_axi_fifo.test_bench_axi_fifo_sim("tests/axi_fifo_sim")
Signal_Variable_class.var_sig_tb_2vhdl("tests/var_sig_class")
#Signal_Variable_class.var_sig_tb_sim("tests/var_sig_class_sim")