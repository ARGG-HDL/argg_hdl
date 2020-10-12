import argparse
import os,sys,inspect
import copy

from argg_hdl.argg_hdl_base import *
from argg_hdl.argg_hdl_v_Package import *
from argg_hdl.argg_hdl_v_class import *
from argg_hdl.argg_hdl_v_class_trans import *
from argg_hdl.argg_hdl_master_slave import *
from argg_hdl.converter.argg_hdl_v_class_trans_converter import v_class_trans_converter


class axisStream_converter(v_class_trans_converter):
    def __init__(self):
        super().__init__()


    def def_includes(self,obj, name,parent):
        ret =""
        typeName = obj.data.__hdl_converter__.get_type_simple(obj.data)
        
        depobj  = obj.__hdl_converter__.get_dependency_objects(obj,[])
        
        ret += "use work.axisStream_"+str(typeName)+".all;\n"
        members = obj.getMember() 
        for x in members:
            ret += x["symbol"].__hdl_converter__.def_includes(x["symbol"],name,parent)

        return ret
    
    def get_packet_file_name(self, obj):
        typeName = obj.data.__hdl_converter__.get_type_simple(obj.data)
        return "axisStream_"+str(typeName)+".vhd"

    def get_packet_file_content(self, obj):
        typeName = obj.data.__hdl_converter__.get_type_simple(obj.data)
        pack =  "axisStream_"+str(typeName)

        fileContent = make_package(pack,  obj.data)
        return fileContent

class axisStream(v_class_trans):
    def __init__(self,Axitype):
        super().__init__("axiStream_"+Axitype.__hdl_converter__.get_type_simple(Axitype))
        self.__hdl_converter__ =axisStream_converter()
        AddDataType( v_copy( Axitype ) )
        self.valid  = port_out( v_sl() )
        self.last   = port_out( v_sl() )
        self.data   = port_out(  Axitype   )
        self.ready  = port_in( v_sl() )

    def get_master(self):
        return axisStream_master(self)

    def get_slave(self):
        return axisStream_slave(self)

class axisStream_slave_converter(v_class_slave_converter):
    def __init__(self):
        super().__init__()

    def def_includes(self,obj, name,parent):
        ret =""
        typeName = obj.data.__hdl_converter__.get_type_simple(obj.data)
        
        depobj  = obj.__hdl_converter__.get_dependency_objects(obj,[])
        
        ret += "use work.axisStream_"+str(typeName)+".all;\n"
        members = obj.getMember() 
        for x in members:
            ret += x["symbol"].__hdl_converter__.def_includes(x["symbol"],name,parent)

        return ret
    
    def get_packet_file_name(self, obj):
        typeName = obj.data.__hdl_converter__.get_type_simple(obj.data)
        return "axisStream_"+str(typeName)+".vhd"

    def get_packet_file_content(self, obj):
        typeName = obj.data.__hdl_converter__.get_type_simple(obj.data)
        pack =  "axisStream_"+str(typeName)

        fileContent = make_package(pack,  obj.data)
        return fileContent

    def _to_hdl___bool__(self, obj, astParser):
        hdl = obj.__hdl_converter__._vhdl__call_member_func(obj, "isReceivingData",[obj],astParser)

        if hdl is None:
            astParser.Missing_template=True
            return "-- $$ template missing $$"
        return hdl

    def impl_get_value(self,obj, ReturnToObj=None,astParser=None):

        vhdl_name = str(obj) + "_buff"
        buff =  astParser.try_get_variable(vhdl_name)

        if buff is None:
            buff = v_copy(obj.rx.data)
            buff.__hdl_name__ = str(obj) + "_buff"
            buff.__hdl_name__ = buff.__hdl_name__.replace("(","").replace(")","")
            buff._varSigConst = varSig.variable_t
            astParser.LocalVar.append(buff)


        hdl = obj.__hdl_converter__._vhdl__call_member_func(obj, "read_data",[obj, buff],astParser)
        if hdl is None:
            astParser.AddStatementBefore("-- $$ template missing $$")
            astParser.Missing_template=True
            return buff



        astParser.AddStatementBefore(hdl)
        return buff

    def def_includes(self,obj, name,parent):
        

        return ""

    def get_packet_file_name(self, obj):
        ret = obj.rx.__hdl_converter__.get_packet_file_name(obj.rx)
        return ret


    def get_packet_file_content(self, obj):
        ret = obj.rx.__hdl_converter__.get_packet_file_content(obj.rx)
        return ret


class axisStream_slave(v_class_slave):
    def __init__(self, Axi_in):
        super().__init__(Axi_in._type+"_slave")
        self.__hdl_converter__ =axisStream_slave_converter()
        
        self.rx =  variable_port_Slave( Axi_in)
        self.rx  << Axi_in
    
        self.data_isvalid            = v_variable( v_sl() )
        self.data_internal2          = v_variable( Axi_in.data )
        self.data_internal_isvalid2  = v_variable( v_sl())
        self.data_internal_was_read2 = v_variable(v_sl())
        self.data_internal_isLast2   = v_variable( v_sl())
        
        
        
    def observe_data(self, dataOut = variable_port_out(dataType())):
        if self.data_internal_isvalid2:
            dataOut << self.data_internal2
    
    
    def read_data(self, dataOut ):
        if self.data_internal_isvalid2:
            dataOut << self.data_internal2
            self.data_internal_was_read2 << 1
    

    def __rshift__(self, rhs):
        rhs.reset()
        if self.data_internal_isvalid2:
            rhs << self.data_internal2
            self.data_internal_was_read2 << 1

    def isReceivingData(self):
        return  self.data_internal_isvalid2 == 1


    def IsEndOfStream(self):
        return  self.data_internal_isvalid2 > 0 and  self.data_internal_isLast2 > 0

    def __bool__(self):
        return self.isReceivingData()

    def _onPull(self):
        if self.rx.ready and self.rx.valid:
            self.data_isvalid << 1
        
        self.data_internal_was_read2 << 0
        self.rx.ready << 0      
   
        if self.data_isvalid  and not self.data_internal_isvalid2:
            self.data_internal2 << self.rx.data 
            self.data_internal_isvalid2 << self.data_isvalid
            self.data_internal_isLast2 << self.rx.last
            self.data_isvalid << 0


    def _onPush(self):
        if self.data_internal_was_read2:
            self.data_internal_isvalid2 << 0

        if not self.data_isvalid and not self.data_internal_isvalid2:
            self.rx.ready << 1
        
    def _sim_get_value(self):
        if self.data_internal_isvalid2:
            self.data_internal_was_read2 << 1

        return self.data_internal2._sim_get_value()


class axisStream_master_converter(v_class_master_converter):
    def __init__(self):
        super().__init__()

    def _to_hdl___bool__(self, obj, astParser):
        ret =  obj.__hdl_converter__._vhdl__call_member_func(obj, "ready_to_send",[obj],astParser)
        if ret is None:
            astParser.Missing_template=True
            return "$$missing_template$$"
        return ret
    
    def impl_reasign(self,obj, rhs,astParser,context_str=None):
        ret =  obj.__hdl_converter__._vhdl__call_member_func(obj, "send_data",[obj, rhs],astParser)
        if ret is None:
            astParser.Missing_template=True
            return "$$missing_template$$"
        return ret




    def get_packet_file_name(self, obj):
        ret = obj.tx.__hdl_converter__.get_packet_file_name(obj.tx)
        return ret

    def get_packet_file_content(self, obj):
        ret = obj.tx.__hdl_converter__.get_packet_file_content(obj.tx)
        return ret


    def def_includes(self,obj, name,parent):
        ret = obj.tx.__hdl_converter__.def_includes(obj.tx, name, parent)
        return ret


class axisStream_master(v_class_master):
    def __init__(self, Axi_Out):
        super().__init__(Axi_Out._type + "_master")
        self.__hdl_converter__ =axisStream_master_converter()
        self.tx =  variable_port_Master( Axi_Out)
        Axi_Out  << self.tx


   
    def reset(self):
        self.tx.valid   << 0

        
    def send_data(self, dataIn ):
        self.tx.valid   << 1
        self.tx.data    << dataIn    
    
    def ready_to_send(self):
        return not self.tx.valid

    def Send_end_Of_Stream(self, EndOfStream=True):
        if EndOfStream:
            self.tx.last << 1
        else:
            self.tx.last << 0


    def _onPull(self):

        if self.tx.ready: 
            self.tx.valid.reset()
            self.tx.last.reset()
            self.tx.data.reset()

    
    def __lshift__(self, rhs):
        self.send_data(value(rhs))

    def __bool__(self):
        
        return self.ready_to_send()





def make_package(PackageName,AxiType):
    s = isConverting2VHDL()
    ax_t = axisStream(AxiType)
    ax_m = axisStream_master(ax_t)
    ax_s = axisStream_slave(ax_t)
    set_isConverting2VHDL(True)

    
    ax = v_package(PackageName,sourceFile=__file__,
    PackageContent = [
        ax_t,
        ax_m,
        ax_s,
        #axisStream_slave_signal(ax_t)
        #axisStream_master_with_strean_counter(ax_t)
    ]
    
    
    )
    fileContent = ax.to_string()
    set_isConverting2VHDL(s)
    return fileContent
