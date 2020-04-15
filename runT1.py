import argg_hdl.tests.RamHandler as RamHandler
from argg_hdl.tests.helpers  import remove_old_files


remove_old_files()
RamHandler.RamHandler_2vhdl("tests/RamHandler")