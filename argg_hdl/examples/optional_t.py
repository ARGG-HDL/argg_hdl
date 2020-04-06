from argg_hdl import *
from  argg_hdl.examples import *




class optional_t(v_class_master):
    def __init__(self,DataType= v_slv(32)):
        super().__init__()
        self.data = v_variable(DataType)
        self.valid = v_variable(v_sl())

    def get_data(self, data):
        if self.valid:
            data << self.data


    def __rshift__(self, rhs):
        rhs.reset()
        if self.valid:
            rhs << self.data


    def is_valid(self):
        return self.valid == 1
    
    def reset(self):
        self.valid << 0
    
    def set_inValid(self):
        self.valid << 0

    def set_data(self, data):
        self.valid << 1
        self.data << data

    def __lshift__(self,rhs):
        self.valid << 1
        self.data << rhs

    def __bool__(self):
        return self.is_valid()
