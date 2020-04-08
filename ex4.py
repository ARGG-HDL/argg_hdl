from argg_hdl import *
from  argg_hdl.examples import *

class tb(v_entity):
    def __init__(self):
        super().__init__()
        self.clk = port_in(v_sl())
        self.data_in = port_Slave(axisStream(v_slv(32)))
        self.data_out = port_Master(axisStream( v_slv(32)))
        self.architecture()


    @architecture
    def architecture(self):
        
        data_buffer = v_slv(32)
        v_data_buffer = v_variable(v_slv(32))
        d_out = get_handle(self.data_out)
        d_in = get_handle(self.data_in)

        memo = v_list(v_slv(32), 100)

        counter1 = v_slv(32)
        counter2  = v_slv(32)
        op_data = optional_t(v_slv())
        @rising_edge(self.clk)
        def proc():

            if d_in:
                d_in >> op_data 
                op_data >>  memo[counter1] 


            if d_out:
                d_out << memo[counter2]
                counter2 << counter2 + 1

            if counter2 > len(memo):
                counter2 << 0


        end_architecture()




tb1 = v_create(tb())
convert_to_hdl(tb1,"ex4")