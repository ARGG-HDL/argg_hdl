from argg_hdl.argg_hdl_base import *
from argg_hdl.argg_hdl_v_function import *
from argg_hdl.argg_hdl_v_entity_list import *

import argg_hdl.argg_hdl_v_Package as argg_pack

from argg_hdl.argg_hdl_v_class import  v_class
from argg_hdl.argg_hdl_v_class_handle import  v_class_hanlde
from argg_hdl.argg_hdl_object_factory import add_constructor
from argg_hdl.converter.argg_hdl_v_class_handle_converter import v_class_hanlde_converter


class v_class_master_converter(v_class_hanlde_converter):
    def __init__(self):
        super().__init__()


class v_class_master(v_class_hanlde):

    def __init__(self,Name=None,varSigConst=None):
        super().__init__(Name,varSigConst)
        self.__hdl_converter__ = v_class_master_converter()
        self.__v_classType__  = v_classType_t.Master_t



class v_class_slave_converter(v_class_hanlde_converter):
    def __init__(self):
        super().__init__()


class v_class_slave(v_class_hanlde):

    def __init__(self,Name=None,varSigConst=None):
        super().__init__(Name,varSigConst)
        self.__hdl_converter__ = v_class_slave_converter()
        self.__v_classType__  = v_classType_t.Slave_t



def get_master(transObj):
    return transObj.get_master()

def get_salve(transObj):
    return transObj.get_slave()

def get_handle(transObj):
    if transObj._Inout == InOut_t.Slave_t:
        return get_salve(transObj)
    
    if transObj._Inout  == InOut_t.Master_t:
        return get_master(transObj)
    
    raise Exception("Unable to determint requiered handle")


add_constructor("v_class_slave", v_class_slave)
add_constructor("v_class_master",v_class_master)
