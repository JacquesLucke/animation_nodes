import bpy

listChains = [
    ["mn_FloatSocket", "mn_FloatListSocket"],
    ["mn_IntegerSocket", "mn_IntegerListSocket"],
    ["mn_VectorSocket", "mn_VectorListSocket"],
    ["mn_ObjectSocket", "mn_ObjectListSocket"],
    ["mn_StringSocket", "mn_StringListSocket"],
    ["mn_VertexSocket", "mn_VertexListSocket"],
    ["mn_PolygonSocket", "mn_PolygonListSocket"],
    ["mn_EdgeIndicesSocket", "mn_EdgeIndicesListSocket"],
    ["mn_PolygonIndicesSocket", "mn_PolygonIndicesListSocket"],
    ["mn_ParticleSocket", "mn_ParticleListSocket"],
    ["mn_ParticleSystemSocket", "mn_ParticleSystemListSocket"],
    ["mn_SplineSocket", "mn_SplineListSocket"] ]

def getListBaseSocketIdName(idName):
    for listChain in listChains:
        if idName in listChain:
            index = listChain.index(idName)
            if index == 0: return None
            else: return listChain[index - 1]

def getListSocketIdName(idName):
    for listChain in listChains:
        if idName in listChain:
            index = listChain.index(idName)
            if index == len(listChain) - 1: return None
            return listChain[index + 1]
    return None

def isListSocketIdName(socketType):
    return not getListBaseSocketIdName(socketType) == None

def hasListSocket(socketType):
    return not getListSocketIdName(socketType) == None

def getIdNameFromDataType(dataType):
    for subClass in getSocketClasses():
        if getattr(subClass, "dataType") == dataType: return subClass.bl_idname
    return None

def getDataTypeFromIdName(idName):
    cls = getattr(bpy.types, idName)
    return cls.dataType

def getSocketClassFromIdName(idName):
    for cls in getSocketClasses():
        if cls.bl_idname == idName: return cls
    return None

def getListBaseSocketIdNames():
    idNames = []
    for listChain in listChains:
        idNames.extend(listChain[:-1])
    return idNames

def getListSocketIdNames():
    types = []
    for listChain in listChains:
        for i, type in enumerate(listChain):
            if i > 0:
                types.append(type)
    return types

def getSocketDataTypeItems(self, context):
    socketNames = getSocketDataTypes()
    socketNames.sort()
    return [(name, name, "") for name in socketNames]

def getSocketDataTypes():
    return [socketClass.dataType for socketClass in getSocketClasses()]

def getSocketClasses():
    from .. import mn_node_base
    return mn_node_base.mn_BaseSocket.__subclasses__()
