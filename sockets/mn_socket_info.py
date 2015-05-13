listChains = [
    ["mn_FloatSocket", "mn_FloatListSocket"],
    ["mn_VectorSocket", "mn_VectorListSocket"],
    ["mn_ObjectSocket", "mn_ObjectListSocket"],
    ["mn_StringSocket", "mn_StringListSocket"],
    ["mn_VertexSocket", "mn_VertexListSocket"],
    ["mn_PolygonSocket", "mn_PolygonListSocket"],
    ["mn_EdgeIndicesSocket", "mn_EdgeIndicesListSocket"],
    ["mn_PolygonIndicesSocket", "mn_PolygonIndicesListSocket"],
    ["mn_ParticleSocket", "mn_ParticleListSocket"],
    ["mn_ParticleSystemSocket", "mn_ParticleSystemListSocket"]]
    
def getBaseSocketType(socketType):
    for listChain in listChains:
        if socketType in listChain:
            index = listChain.index(socketType)
            if index == 0: return None
            else: return listChain[index - 1]
    
def getListSocketType(socketType):
    for listChain in listChains:
        if socketType in listChain:
            index = listChain.index(socketType)
            if index == len(listChain) - 1: return None
            return listChain[index + 1]
    return None
    
def isListSocketType(socketType):
    return not getBaseSocketType(socketType) == None
    
def hasListSocketType(socketType):
    return not getListSocketType(socketType) == None
    
def getSocketNameByDataType(dataType):
    for subClass in getSocketClasses():
        if getattr(subClass, "dataType") == dataType: return subClass.bl_idname
    return None
    
def getListDataTypes():
    types = []
    for listChain in listChains:
        for i, type in enumerate(listChain):
            if i > 0:
                types.append(type)
    return types

def getSocketNameItems(self, context):
    socketNames = getSocketNames()
    socketNames.sort()
    return [(name, name, "") for name in socketNames]
        
def getSocketNames():
    return [socketClass.dataType for socketClass in getSocketClasses()]
    
def getSocketClasses():
    from .. import mn_node_base
    return mn_node_base.mn_BaseSocket.__subclasses__()