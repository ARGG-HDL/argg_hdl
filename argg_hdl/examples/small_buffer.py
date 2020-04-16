from argg_hdl import *
from  argg_hdl.examples import *



class small_buffer(v_class_master):
    def __init__(self,DataType= v_slv(32),NumElements=10):
        super().__init__()
        self._varSigConst = varSig.variable_t
        self.mem       = v_variable(v_list(v_copy(DataType),NumElements))
        self.head      = v_variable(v_int())
        self.tail      = v_variable(v_int())
        self.tail_old  = v_variable(v_int())
        self.count     = v_variable(v_int())
        self.count_old = v_variable(v_int())


    def isReceivingData(self):
        return self.count > 0
    

    def re_read(self):
        self.tail  << self.tail_old
        self.count << self.count_old

    def read_data(self, data):
        data.reset()

        if self.count > 0:
            data << self.mem[self.tail]
            self.tail << self.tail + 1
            self.count << self.count - 1
        

        if self.tail > len(self.mem) - 1:
            self.tail << 0 

    def __rshift__(self, rhs):
        rhs.reset()

        if self.count > 0:
            rhs << self.mem[self.tail]
            self.tail << self.tail + 1
            self.count << self.count - 1
        

        if self.tail > len(self.mem) - 1:
            self.tail << 0 

    def send_data(self, data):
        if self.ready_to_send():
            self.mem[self.head] << data 
            self.head << self.head + 1
            self.count << self.count + 1
            if self.head > len(self.mem) - 1:
                self.head << 0 
        
        self.tail_old << self.tail
        self.count_old << self.count
                
    def __lshift__(self,rhs):
        
        if self.ready_to_send():
            self.mem[self.head] << rhs 
            self.head << self.head + 1
            self.count << self.count + 1
            if self.head > len(self.mem) - 1:
                self.head << 0 
        
        self.tail_old << self.tail
        self.count_old << self.count

    def length(self):
        return len(self.mem)

    def ready_to_send(self):
        return self.count < len(self.mem)

    def __len__(self):
        return len(self.mem)

    def reset(self):
        self.head  << 0
        self.tail  << 0
        self.count << 0