import argg_hdl.tests
from argg_hdl.tests.helpers  import remove_old_files
import argg_hdl.argg_hdl_test_handler as argg_test

remove_old_files()

argg_test.run_all_tests()
#result, message = argg_test.run_test('fifo_cc_tb_sim')
#print(result , message)
