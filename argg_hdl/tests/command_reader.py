
from argg_hdl.argg_hdl_base import end_constructor
from argg_hdl import *
from  argg_hdl.examples import *

from .helpers import Folders_isSame, vhdl_conversion, do_simulation,printf
from argg_hdl.argg_hdl_test_handler import add_test

from enum import Enum, auto


class command_reader(v_clk_entity):
    def __init__(self,clk) -> None:
        super().__init__(clk)
        self.Ax_in       = pipeline_in(axisStream(v_slv(32)))
        self.Ax_data_out = pipeline_out(axisStream(v_slv(32)))
        self.architecture()

    @architecture
    def architecture(self):
        cmd = command_handler_base(self.clk,  reg_handle() ) 
        self.Ax_in \
            | cmd \
            | \
        self.Ax_data_out
        
        end_architecture()


class state_t(Enum):
    idle = auto()
    proce = auto()
    passthrough = auto()

class command_handler_base(v_clk_entity):
    def __init__(self, clk, DevHandle) -> None:
        super().__init__(clk)
        self.Ax_in       = pipeline_in(axisStream(v_slv(32)))
        self.Ax_out      = pipeline_out(axisStream(v_slv(32)))
        self.DevHandle   =  port_out(DevHandle)
        self.architecture()


    


    @architecture
    def architecture(self):
        Target_device =  get_handle(self.DevHandle)
        data_in = get_handle(self.Ax_in)
        data_out = get_handle(self.Ax_out)
        buff = v_variable(v_slv(32))
        state = v_variable(v_enum(state_t.idle))

        @rising_edge(self.clk)
        def proc():
            if data_in:
                if state == state_t.idle:
                    data_in >> buff
                    if Target_device.isThisHeader(buff):
                        state << state_t.proce
                    else:
                        state << state_t.passthrough
                
            if state == state_t.proce:
                Target_device.process_event(data_in, data_out)
                if Target_device.isDone():
                    state << state_t.idle
                    data_out.Send_end_Of_Stream()

            elif state == state_t.passthrough:
                if data_in and data_out:
                    data_in >> data_out
                
                if data_in.IsEndOfStream():
                    state << state_t.idle

        end_architecture()


class reg_package(v_record):
    def __init__(self):
        super().__init__()
        self.key1 = v_slv(32)
        self.key2 = v_slv(32)
        self.key3 = v_slv(32)
        self.key4 = v_slv(32)
        self.isComplete = v_sl()

    def deserialize(self, buff, counter):
        if counter == 0:
            self.key1 << buff
        elif counter == 1:
            self.key2 << buff
        elif counter == 2:
            self.key3 << buff
        elif counter == 3:
            self.key4 << buff
            self.isComplete << 1



class reg_handle(v_class_trans):
    def __init__(self) -> None:
        super().__init__()
        self.addr     = port_out(v_slv(32))
        self.data_in  = port_in(v_slv(32))
        self.data_out = port_out(v_slv(32))

    def get_master(self):
        return register_handler_obj(self)

class register_handler_obj(v_class_slave):
    def __init__(self,reg) -> None:
        super().__init__()
        self.reg_ports = variable_port_Master(reg)
        reg << self.reg_ports
        self.reg = v_variable(reg_package())
        self.counter = v_variable(v_slv(32))
        self.Done = v_variable(v_sl())

    def process_event(self, ax_in, ax_out):
        self.Done <<0
        buff = v_slv(32)
        if ax_in and ax_out:
            ax_in >> buff
            self.reg.deserialize(buff, self.counter)
            self.counter <<  self.counter + 1
            if self.reg.isComplete:
                ax_out << 0x123
            else:
                ax_out << 0x123456
            if ax_in.IsEndOfStream():
                self.Done <<1
                



    def isThisHeader(self, buff):
        return buff == 0x12345678

    def isDone(self):
        return self.Done>0


    

class cmd_tb(v_entity):
    def __init__(self) -> None:
        super().__init__()
        self.architecture()

    @architecture
    def architecture(self):
        clkgen = clk_generator()
        cmd = command_reader(clkgen.clk)
        
        ax_in = get_handle(cmd.Ax_in)
        counter = v_slv(32)
        
        @rising_edge(clkgen.clk)
        def proc():
            cmd.Ax_data_out.ready << 1
            counter << counter +1
            if counter== 10:
                ax_in << 0x12345678
            
            if counter > 10:
                ax_in << counter
            
            if counter == 20:
                ax_in.Send_end_Of_Stream()
                
                

        end_architecture()



@do_simulation
def cmd_tb_sim(OutputPath, f= None):
    
    tb1 = cmd_tb()
    return tb1
def test_cmd_tb_sim():
    return cmd_tb_sim("tests/cmd_tb_sim") 

add_test("cmd_tb_sim", test_cmd_tb_sim)
        


@vhdl_conversion
def cmd_tb_2vhdl(OutputPath, f= None):
    
    tb1 = cmd_tb()
    return tb1


def test_cmd_tb_2vhdl():
    return cmd_tb_2vhdl("tests/cmd_tb/") 

add_test("cmd_tb_2vhdl", test_cmd_tb_2vhdl)