from argg_hdl import *
from  argg_hdl.examples import *

class axiStreamMux(v_entity):
    def __init__(self, clk):
        super().__init__()
        self.clk = port_in(v_sl())
        self.clk << clk
        self.data_in = port_Slave(v_list(axisStream(v_slv(32)),4))
        self.data_out = port_Master(axisStream( v_slv(32)))
        self.architecture()


    @architecture
    def architecture(self):
        d_in = get_handle(self.data_in)
        d_out = get_handle(self.data_out)

        data_buffer = v_slv(32)
        ChannelUsed = v_int()
        sending= v_sl()
        @rising_edge(self.clk)
        def proc():
            if not sending:
                for i12 in range(len(d_in)):
                    if i12 == ChannelUsed:
                        ChannelUsed << len(d_in) + 1
                        continue

                    if d_in[i12] and d_out:
                        ChannelUsed << i12
                        d_in[i12] >> data_buffer
                          
                        d_out.Send_end_Of_Stream(d_in[i12].IsEndOfStream())
                        if not d_in[i12].IsEndOfStream():
                            sending << 1
                        break

            elif sending and  d_in[ChannelUsed] and d_out:
                d_in[ChannelUsed] >> d_out
                d_out.Send_end_Of_Stream(d_in[ChannelUsed].IsEndOfStream())
                if d_in[ChannelUsed].IsEndOfStream():
                    sending << 0

        end_architecture()


class d_source(v_entity):
    def __init__(self, clk):
        super().__init__()
        self.clk = port_in(clk)
        self.clk << clk
        self.data_out = port_Master(axisStream( v_slv(32)))
        self.architecture()
    
    @architecture
    def architecture(self):
        
        
        end_architecture()

class memo(v_class_master):
    def __init__(self):
        super().__init__()
        self.l= v_signal(v_list(v_slv(32),100))
    
    def set_data(self, data):
        self.l[0] << data
    
    def get_data(self, data):
        data << self.l[0]
    

class tb(v_entity):
    def __init__(self):
        super().__init__()
        self.architecture()


    @architecture
    def architecture(self):
        clkgen = v_create( clk_generator()) 
        axmux = v_create(axiStreamMux(clkgen.clk))
        d_s   = v_create(d_source(clkgen.clk))
        axmux.data_in[0] << d_s.data_out

        m = memo()
        d = v_slv(32)
        d2 = v_slv(32)
        
        @rising_edge(clkgen.clk)
        def proc():
            m.set_data(d)
            m.get_data(d2)
        
        end_architecture()






tb1 = v_create(tb())
convert_to_hdl(tb1,"ex4")