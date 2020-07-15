from enum import Enum 

class  InOut_t(Enum):
    input_t    = 1
    output_t   = 2    
    Internal_t = 3
    Master_t   = 4
    Slave_t    = 5
    InOut_tt   = 6
    Default_t  = 7
    Unset_t    = 8 
    Used_t     = 9 

    def __repr__(self):
        return str(self).split(".")[-1]

class varSig(Enum):
    variable_t = 1
    signal_t =2 
    const_t =3
    reference_t = 4
    combined_t = 5
    unnamed_const = 6
    runtime_variable_t =7 
    

    def __repr__(self):
        return str(self).split(".")[-1]

v_defaults ={
"defVarSig" : varSig.variable_t
}


def getDefaultVarSig():
    return v_defaults["defVarSig"]

def setDefaultVarSig(new_defVarSig):
    v_defaults["defVarSig"] = new_defVarSig

def get_varSig(varSigConst):
    if varSigConst == varSig.signal_t:
        return "signal"
    
    if varSigConst == varSig.variable_t:
        return  "variable"
    
    if varSigConst == varSig.const_t:
        return  "constant"

    raise Exception("unknown type")


def Inout_add_input(Inout=InOut_t.Internal_t):
    ret = Inout
    if ret is None:
        ret = InOut_t.input_t
    elif ret == InOut_t.Internal_t:
        ret = InOut_t.input_t
    elif ret == InOut_t.output_t:
        ret = InOut_t.InOut_tt
    elif ret == InOut_t.Used_t:
        ret = InOut_t.input_t
    return ret

def Inout_add_output(Inout=InOut_t.Internal_t):
    ret = Inout
    if ret is None:
        ret = InOut_t.output_t
    elif ret == InOut_t.Internal_t:
        ret = InOut_t.output_t
    elif ret == InOut_t.input_t:
        ret = InOut_t.InOut_tt
    elif ret == InOut_t.Used_t:
        ret = InOut_t.output_t
    return ret

def Inout_add_used(Inout=InOut_t.Internal_t):
    ret = Inout
    if ret is None:
        ret = InOut_t.Used_t
    elif ret == InOut_t.Internal_t:
        ret = InOut_t.Used_t
    elif ret == InOut_t.Unset_t:
        ret = InOut_t.Used_t
    return ret


def InoutFlip(inOut):
    if inOut == InOut_t.input_t:
        return InOut_t.output_t
    
    if inOut ==   InOut_t.output_t:
        return InOut_t.input_t
    
    if inOut == InOut_t.Master_t:
        return InOut_t.Slave_t
    
    if inOut == InOut_t.Slave_t:
        return InOut_t.Master_t

    return inOut

class v_classType_t(Enum):
    transition_t = 1
    Master_t = 2
    Slave_t = 3
    Record_t =4
    
    def __repr__(self):
        return str(self).split(".")[-1]