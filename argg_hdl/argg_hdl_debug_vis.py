import json as js


def unfold_drivers(obj):
    ret =[]
    if obj.__Driver__ != None:
        ret.append(obj.__Driver__)
        ret += unfold_drivers(obj.__Driver__)

    return ret

class DebugGraph:
    def __init__(self):
        super().__init__()
        self.id = 0
        self.Entity_list= []
        
        
        
    def append(self, x):
        if not x._issubclass_("v_entity"):
            return 
        self.Entity_list.append({
            "id" : str(self.id),
            "symbol": x
        })
        self.id += 1
    
    def add_nodes(self,EntityGraph):
        for x in self.Entity_list:
            EntityGraph["nodes"].append({"id": x["id"], "label": type(x["symbol"]).__name__})
        
        
        return EntityGraph


    def find_connections(self,Obj):
        ret =[]
        mem2 = Obj["symbol"].getMember()
        for x in self.Entity_list:
            mem = x["symbol"].getMember()
            for m in mem:
                drivers = unfold_drivers(m["symbol"])
                for m2 in mem2:
                    if m["symbol"].__Driver__ is m2["symbol"]:
                        ret.append({"from": Obj["id"], "to": x["id"]})

        return ret

    def add_edges(self,EntityGraph):
        for x in self.Entity_list:
            connections = self.find_connections(x)
            EntityGraph["edges"] += connections
        return EntityGraph


    def js_dumb(self):

        EntityGraph = {
            "kind": {"graph": True},
            "nodes": [],
            "edges": []
        }
        EntityGraph = self.add_nodes(EntityGraph)
        EntityGraph = self.add_edges(EntityGraph)

        json_graph = js.dumps(EntityGraph)
        return json_graph

gDebugGraph = DebugGraph()

def append(obj):
    gDebugGraph.append(obj)

def js_dumb():
    return gDebugGraph.js_dumb()
    