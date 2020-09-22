gStatus = {
    "isConverting2VHDL" : False,
    "isProcess" : False,
    "isPrimaryConnection" : True,
    "MakeGraph"           : True,
    "saveUnfinishFiles"   : False,
    "OutputFile"          : None,
    "isFunction"          : False,
    "sort_archetecture"   : False,
    "isRunning"           : False,
    'Output_HDL'          : "VHDL"
} 

def isFunction():
    return gStatus["isFunction"]
    
def set_isFunction(newState):
    gStatus["isFunction"]  =   newState

def isConverting2VHDL():
    return gStatus["isConverting2VHDL"]

def set_isConverting2VHDL(newStatus):
    gStatus["isConverting2VHDL"] = newStatus

def isProcess():
    return gStatus["isProcess"]

def set_isProcess(newStatus):
    gStatus["isProcess"] = newStatus

def isPrimaryConnection():
    return gStatus["isPrimaryConnection"]

def set_isPrimaryConnection(newStatus):
    gStatus["isPrimaryConnection"] = newStatus

def MakeGraph():
    return gStatus["MakeGraph"]

def set_MakeGraph(newState):
    gStatus["MakeGraph"]  = newState

def saveUnfinishedFiles():
    return gStatus["saveUnfinishFiles"]

def sort_archetecture():
    return gStatus["sort_archetecture"]

def set_sort_archetecture(newState):
    gStatus["sort_archetecture"]  = newState


def isRunning():
    return gStatus["isRunning"]

def set_isRunning(newState):
    gStatus["isRunning"]  = newState

def Output_HDL():
    return gStatus["Output_HDL"]


def set_Output_HDL(newTarget):
    gStatus["Output_HDL"] = newTarget


def print_cnvt_set_file(FileName=None):
    
    if gStatus["OutputFile"] is not None:
        gStatus["OutputFile"].close()
        gStatus["OutputFile"] = None

    if FileName is not None:
        gStatus["OutputFile"] = open(FileName,"w",newline="")
    else:
        gStatus["OutputFile"] = None
        

def print_cnvt(Str_in):
    if gStatus["OutputFile"] is not None:
        gStatus["OutputFile"].write(Str_in +"\n")
    else:
        print(Str_in)