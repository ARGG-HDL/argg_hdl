


from argg_hdl.argg_hdl_base import *
from argg_hdl.argg_hdl_v_symbol import *

from argg_hdl.argg_hdl_simulation import *
from argg_hdl.argg_hdl_v_entity import *
from argg_hdl.argg_hdl_v_class import *
from argg_hdl.argg_hdl_v_record import *
from argg_hdl.argg_hdl_v_list import *
from argg_hdl.argg_hdl_master_slave import *


class register_t(v_record):
    def __init__(self):
        super().__init__()
        self.address   = v_slv(16) 
        self.value     = v_slv(16) 
    
    def get_value(self, addr, data):
        if self.address == addr: 
            self.value >> data



class system_globals(v_record):
    def __init__(self):
        super().__init__()
        self.clk   =  v_sl() 
        self.clk.__isFreeType__ = True
        self.rst   =  v_sl() 
        self.reg   =  register_t() 



class system_globals_delay(v_entity):
    def __init__(self, gSystem=system_globals()):
        super().__init__()
        self.gSystem      = port_in(gSystem)
        self.gSystem      << gSystem
        self.register_out = port_out(register_t())
        self.architecture()

    @architecture
    def architecture(self):

        reg_out1 =v_signal(register_t())
        reg_out2 = v_signal(register_t())
        reg_out3 = v_signal(register_t())
        reg_out4 =v_signal( register_t())

        @rising_edge(self.gSystem.clk)
        def proc():
            reg_out1      << self.gSystem.reg 
            reg_out2      << reg_out1
            reg_out3      << reg_out2
            reg_out4      << reg_out3
            self.register_out  << reg_out4

        end_architecture()


class register_handler(v_class_master):
    def __init__(self,gSystem = system_globals()):
        super().__init__()
        self.__hdl_useDefault_value__ = False
        self.gSystem  = system_globals()
        self.gSystem  << gSystem
        self.localStorage_addr = v_list( v_slv(16) , 0 , varSig.signal_t)
        self.localStorage_value = v_list( v_slv(16) , 0 , varSig.signal_t)
        self.architecture()    

    def get_register(self, RegisterAddres):
        reg = v_slv(16)
        reg << RegisterAddres
        val = v_slv(16)
        self.localStorage_addr.append(reg)
        self.localStorage_value.append(val)
        return val




    @architecture
    def architecture(self):

        registers = system_globals_delay(self.gSystem)

        @rising_edge(self.gSystem.clk)
        def proc_register_handler():
            for index  in  range( len(self.localStorage_addr)) :
                if registers.register_out.address == self.localStorage_addr[index]:
                    self.localStorage_value[index] << registers.register_out.value

        end_architecture()



class register_storage(v_class_master):
    def __init__(self,clk):
        super().__init__()
        self.__hdl_useDefault_value__ = False
        self.gSystem = v_signal( system_globals())
        self.gSystem.clk << clk
        self.localStorage = v_list( register_t() , 0 , varSig.signal_t)
        self.architecture()    
    
    def set_register(self, RegisterAddres, regVal):
        for e in self.localStorage:
            if e.address == RegisterAddres:
                e.value << regVal
                return

        reg =  register_t()
        reg.address << RegisterAddres
        reg.value << regVal
        self.localStorage.append(reg)
        


    @architecture
    def architecture(self):

        cnt = v_slv(32)

        @rising_edge(self.gSystem.clk)
        def proc_register_handler():
            
            cnt << cnt +1
            if cnt < len(self.localStorage):
                self.gSystem.reg << self.localStorage[cnt]
            else:
               cnt << 0 

        end_architecture()