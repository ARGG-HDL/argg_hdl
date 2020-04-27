
from argg_hdl.argg_hdl_base import *


class v_slice_base:
    def __init__(self,symbol, sliceObj):
        super().__init__()
        self.symbol = symbol 
        self.slice = sliceObj

    def get_value(self):
        bitSize = value(self.slice.stop) - value(self.slice.start )
        return 2**bitSize-1 &  ( value(self.symbol) >>value(self.slice.start ))


    def __lshift__(self, rhs):
        bitSize = value(self.slice.stop) - value(self.slice.start )
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




