from  argg_hdl.argg_hdl_base import argg_hdl_base,argg_hdl_base0,argg_hdl_base,architecture,end_architecture
from  argg_hdl.argg_hdl_base import InOut_t,varSig,v_classType_t,v_dataObject,v_variable,v_signal,v_const
from  argg_hdl.argg_hdl_base import port_out, variable_port_out, port_in, variable_port_in, port_Master, variable_port_Master, pipeline_in
from  argg_hdl.argg_hdl_base import  pipeline_out, signal_port_Master, port_Stream_Master, signal_port_Slave, port_Slave, variable_port_Slave
from  argg_hdl.argg_hdl_base import port_Stream_Slave, v_copy, convert_to_hdl, value, print_cnvt_set_file
from  argg_hdl.argg_hdl_v_symbol import v_bool, v_sl ,v_slv, v_int , v_signed , v_unsigned, resize, v_symbol,v_symbol_reset
import argg_hdl.argg_hdl_v_symbol as  ahb
from  argg_hdl.argg_hdl_v_list import v_list

from  argg_hdl.argg_hdl_v_entity import  process , timed , v_create, wait_for, combinational, v_switch , v_case, rising_edge, v_entity  ,v_clk_entity 
from  argg_hdl.argg_hdl_v_entity_list import v_entity_list

from  argg_hdl.argg_hdl_v_class  import v_class
from  argg_hdl.argg_hdl_v_enum  import v_enum

import argg_hdl.argg_hdl_simulation  as ah_simulation

from argg_hdl.argg_hdl_v_Package  import v_package

from argg_hdl.argg_hdl_v_class_trans import v_class_trans

from argg_hdl.argg_hdl_v_record import v_record, v_data_record

from  argg_hdl.argg_hdl_master_slave import get_master, get_salve, get_handle, v_class_master,v_class_slave
import argg_hdl.converter.argg_hdl__primitive_type_converter_base as hdl_converter_base
import argg_hdl.converter.argg_hdl__primitive_converter_bool as hdl_converter_bool
import argg_hdl.converter.argg_hdl__primitive_converter_integer as hdl_converter_integer
import argg_hdl.converter.argg_hdl__primitive_converter_signed as hdl_converter_signed
import argg_hdl.converter.argg_hdl__primitive_converter_sl as hdl_converter_sl
import argg_hdl.converter.argg_hdl__primitive_converter_sl as hdl_converter_sl
import argg_hdl.converter.argg_hdl__primitive_converter_slv as hdl_converter_slv
import argg_hdl.converter.argg_hdl__primitive_converter_uinteger as hdl_converter_uinteger
import argg_hdl.converter.argg_hdl__primitive_converter_unsigned as hdl_converter_unsigned

import argg_hdl.converter.argg_hdl_v_entity_converter as hdl_v_entity_converter
import argg_hdl.converter.argg_hdl_v_list_converter as hdl_v_list_converter
import argg_hdl.converter.argg_hdl_v_record_converter as hdl_v_record_converter
import argg_hdl.converter.argg_hdl_v_class_handle_converter as hdl_v_class_handle_converter
import argg_hdl.converter.argg_hdl_v_class_trans_converter as hdl_v_class_trans_converter

import argg_hdl.converter.argg_hdl_v_free_function_template_converter as argg_hdl_v_free_function_template_converter
import argg_hdl.converter.argg_hdl_v_entity_list_converter as hdl_v_entity_list_converter
import argg_hdl.converter.argg_hdl_v_enum_converter as hdl_v_enum_converter
import argg_hdl.converter.argg_hdl_hdl_converter_base as hdl_hdl_converter_base
import argg_hdl.converter.argg_hdl_v_package_converter as hdl_v_package_converter
import argg_hdl.converter.argg_hdl_v_function_converter as hdl_v_function_converter












## argg_hdl_v_entity



## v_entity_list





## argg_hdl.argg_hdl_simulation 
#gsimulation = ah_simulation.gsimulation
run_simulation = ah_simulation.run_simulation












def g_global_reset():
    ahb.g_global_reset()
    v_symbol_reset()
    ah_simulation.Simulation_reset()