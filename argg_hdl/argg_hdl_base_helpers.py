
def get_type(symbol):
    if hasattr(symbol, "get_type"):
        return symbol.get_type()
    if symbol is None:
        return "None"
    if symbol["symbol"] is None:
        return "None"
    return symbol["symbol"].get_type()

def get_symbol(symbol):
    if hasattr(symbol, "get_symbol"):
        return symbol.get_symbol()
    if symbol is None:
        return None 
    if type(symbol).__name__ != "dict":
        return None
    if symbol["symbol"] is None:
        return None
    return symbol["symbol"].get_symbol()
    

def flatten_list(In_list):
    ret = []
    for x in  In_list:
        if type(x).__name__ == "list":
            buff = flatten_list(x)
            ret += buff
        else:
            ret.append(x)

    return ret



def join_str(content, start="",end="",LineEnding="",Delimeter="",LineBeginning="", IgnoreIfEmpty=False, RemoveEmptyElements = False):
    ret = ""
    content = flatten_list(content)
    if len(content) == 0 and IgnoreIfEmpty:
        return ret
    
    if len(content) == 0:
        ret += start
        ret += end
        return ret

    ret += start
    if RemoveEmptyElements:
        content = [x for x in content if x]

    for x in content[0:-1]:
        ret += LineBeginning + str(x) + Delimeter + LineEnding
    if len(content) == 0 and IgnoreIfEmpty:
        return ""
    ret += LineBeginning + str(content[-1]) +  LineEnding
    ret += end
    return ret



class indent:
    def __init__(self):
        self.ind = 2

    def inc(self):
        self.ind += 2
    
    def deinc(self):
        self.ind -= 2

    def __str__(self):
        ret  = ''.ljust(self.ind)
        return ret

    def reset(self):
        self.ind = 2


gTemplateIndent = indent()


