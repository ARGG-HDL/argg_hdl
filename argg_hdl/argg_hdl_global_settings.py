gStatus = {
    "isConverting2VHDL" : False,
    "isProcess" : False,
    "isPrimaryConnection" : True,
    "MakeGraph"           : True,
    "saveUnfinishFiles"   : False,
    "OutputFile"          : None,
    "isFunction"          : False,
    "sort_archetecture"   : False,
    "isRunning"           : False
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
