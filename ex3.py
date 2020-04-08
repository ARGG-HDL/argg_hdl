from argg_hdl import *
from  argg_hdl.examples import *

class Counter(v_clk_entity):
    def __init__(self, clk , InputType=v_slv(32)):
        super().__init__(clk)
        self.Data_out = port_Stream_Master(axisStream( InputType))
        self.architecture()

    @architecture
    def architecture(self):
        data = v_slv(32)
        data2 = v_slv(32)
        data_out = get_handle(self.Data_out)
        @rising_edge(self.clk)
        def proc():
            data << data + 1
            if data_out and data > 10:
                data_out << data2
                data2   << data2 + 1
                data << 0

        end_architecture()

class tb(v_entity):
    def __init__(self):
        super().__init__()
        self.architecture()



    @architecture
    def architecture(self):
        clkgen = v_create(clk_generator())
        cnt    = v_create(Counter(clkgen.clk))

        cnt_out = get_handle(cnt.Data_out)
        data = v_slv(32)
        data2 = v_slv(32)
        opt_data = optional_t()
        @rising_edge(clkgen.clk)
        def proc():
            cnt_out >> data
            #cnt_out >> opt_data 
            
           

        end_architecture()

tb1 = v_create(tb())

#run_simulation(tb1, 30000,"optional_t.vcd")
convert_to_hdl(tb1,"ex3")