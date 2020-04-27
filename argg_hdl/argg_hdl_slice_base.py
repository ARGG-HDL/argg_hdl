
from argg_hdl.argg_hdl_base import *

class slice_helper:
    def __init__(self,start=None, stop=None,step=None):
        super().__init__()
        self.start = start
        self.stop  = stop
        self.step  = step


class v_slice_base:
    def __init__(self,symbol, sliceObj):
        super().__init__()
        self.symbol = symbol 
        self.slice = sliceObj

    def get_value(self):
        bitSize = len(self)
        return 2**bitSize-1 &  ( value(self.symbol) >>value(self.slice.start ))


    def __lshift__(self, rhs):
        bitSize = len(self)
        bitMask = 2**bitSize-1 << value(self.slice.start )
        sign = -1 if self.symbol.nextValue  < 0 else 1

        next_temp = abs(self.symbol.nextValue)
        next_temp = next_temp - (next_temp & bitMask)
        v = value(rhs)
        if v < 0:
            raise Exception("Negative Number not supported, in Slice")
        v = (v <<  value(self.slice.start)) & bitMask
        next_temp += v
        self.symbol << sign*next_temp

    def __and__(self, rhs):
        bitShift = len(rhs)
        v  = value(self) << bitShift
        v += value(rhs)
        sl= slice_helper(start=0,stop=len(rhs)+len(self))
        ret = v_slice_base(v,sl)
        return ret
        print(self)

    def __len__(self):
        bitSize = value(self.slice.stop) - value(self.slice.start ) + 1
        return bitSize



