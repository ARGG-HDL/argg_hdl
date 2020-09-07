
g_objects_constructors = {

}


def get_Constructor(typeName):
    return g_objects_constructors[typeName]


def add_constructor(typeName, constructor):
    g_objects_constructors[typeName] = constructor