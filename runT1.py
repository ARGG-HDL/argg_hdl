import argg_hdl.tests.test_axi_fifo as test_axi_fifo
from argg_hdl.tests.helpers  import remove_old_files


remove_old_files()


#test_axi_fifo.test_bench_axi_fifo_sim("tests/axi_fifo_sim")
test_axi_fifo.test_bench_axi_fifo_2vhdl("tests/axi_fifo")