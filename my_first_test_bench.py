from argg_hdl import *
import argg_hdl.examples as  ahe
from enum import Enum, auto

class counter_state(Enum):
    idle = auto()
    running = auto()
    done = auto()

class Counter_cl(v_class_master):
    def __init__(self):
        super().__init__()
        self.counter     = v_variable(v_slv(32))
        self.counter_max = v_variable(v_slv(32))
        self.state = v_variable(v_enum(counter_state.idle))

    def _onPull(self):
        if self.state == counter_state.running:
            self.counter << self.counter + 1

    def count_to_max(self, maxValue):
        if self.state == counter_state.idle:
            self.counter << 0 
            self.counter_max << maxValue
            self.state << counter_state.running

    def isDone(self):
        return self.state == counter_state.done

    def reset(self):
        if self.state == counter_state.done:
            self.state << counter_state.idle

class my_first_test_bench(v_entity):
    def __init__(self):
        super().__init__()
        self.architecture()


    @architecture
    def architecture(self):
        counter = v_variable(v_slv(32))
        max_cnt = v_variable(v_slv(32,300))


        clkgen = v_create(ahe.clk_generator())

        cnt = Counter_cl()



        @rising_edge(clkgen.clk)
        def proc():
            counter << counter + 1
            cnt.count_to_max(max_cnt)
            if cnt.isDone():
                cnt.reset()

           

        end_architecture()


my_first_instance = v_create(my_first_test_bench())

convert_to_hdl(my_first_instance, "myFirst")