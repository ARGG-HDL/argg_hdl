
g_objects_constructors = {

}


def impl_constructor(typeName):
    return g_objects_constructors[typeName]


def add_constructor(typeName, constructor):
    g_objects_constructors[typeName] = constructor
