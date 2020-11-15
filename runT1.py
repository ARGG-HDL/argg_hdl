import argg_hdl.tests
from argg_hdl.tests.helpers  import remove_old_files
import argg_hdl.argg_hdl_test_handler as argg_test

remove_old_files()

argg_test.run_all_tests()
#result, message = argg_test.run_test('trigger_bits_test2vhdl')
#print(result , message)
