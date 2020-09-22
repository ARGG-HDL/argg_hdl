
import debugpy
import ast
import os
import sys
import inspect
import time
from  argg_hdl.argg_hdl_base_helpers import join_str

class argg_hdl_error:
    def __init__(self,FileName,LineNo,Column,typeName, msg):
        super().__init__()
        self.FileName  = FileName
        self.LineNo    = LineNo
        self.Column    = Column
        self._typeName  = typeName
        self.msg       = msg

    def __str__(self):
        ret = 'File "' + self.FileName + '", line ' +str(self.LineNo) + ", Column: " + str(self.Column) +", type: " + self._typeName + ", msg: " + self.msg
        return ret

    def Show_Error(self):
        with open(self.FileName) as f:
            content =  f.readlines()
        
        ROI = content[max(0,self.LineNo-6 ) : self.LineNo]
        ROI=join_str(ROI)
        ROI = ROI.rstrip()
        s = ' ' * self.Column
        ret = [str(self), ROI, s+"^",s+"| error msg: "+self.msg ]
        return ret 