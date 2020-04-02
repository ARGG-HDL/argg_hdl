from argg_hdl import *
from  argg_hdl.examples import *


#tb3 = InputDelay_tb()
#convert_to_hdl(tb3, "pyhdl_waveform")

class tb(v_entity):
    def __init__(self):
        super().__init__(srcFileName=__file__)
        self.architecture()

    @architecture
    def architecture(self):
        clkgen = v_create(clk_generator())
        data = v_slv(32,5)
        @rising_edge(clkgen.clk)
        def proc():
            data << data + 1
           

        end_architecture()


tb1 = v_create(tb())

run_simulation(tb1, 100000 ,"test.vcd")