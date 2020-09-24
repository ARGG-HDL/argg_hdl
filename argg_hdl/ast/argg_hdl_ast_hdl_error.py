import  functools 

from  argg_hdl.argg_hdl_base_helpers import join_str
from argg_hdl.argg_hdl_base import gTemplateIndent


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


def Hanlde_errors(description=""):

    def decorator_Hanlde_errors(func):
        @functools.wraps(func)
        def wrapper_Hanlde_errors(self, *args, **kwargs):
            try:
                
                gTemplateIndent.inc()
                return func(self, *args, **kwargs)
            except Exception as inst:
                err_msg = argg_hdl_error(
                    self.sourceFileName(),
                    self.lineno(), 
                    self.col_offset(),
                    self.Name(), 
                    description
                )
                raise Exception(err_msg,self.freeFunction,inst)
            finally:
                gTemplateIndent.deinc()


        return wrapper_Hanlde_errors
    
    return decorator_Hanlde_errors