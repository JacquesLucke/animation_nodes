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
    ["mn_SplineSocket", "mn_SplineListSocket"],
    ["mn_MatrixSocket", "mn_MatrixListSocket"] ]


# Check if list or base socket exists
def isList(input):
    if not isIdName(input): input = toIdName(input)
    return baseIdNameToListIdName(input) is not None

def isBase(input):
    if not isIdName(input): input = toIdName(input)
    return listIdNameToBaseIdName(input) is not None


# to Base
def toBaseIdName(input):
    if isIdName(input): return listIdNameToBaseIdName(input)
    else: return listDataTypeToBaseIdName(input)

def toBaseDataType(input):
    if isIdName(input): return listIdNameToBaseDataType(input)
    else: return listDataTypeToBaseDataType(input)

# to List
def toListIdName(input):
    if isIdName(input): return baseIdNameToListIdName(input)
    else: return baseDataTypeToListIdName(input)

def toListDataType(input):
    if isIdName(input): return baseIdNameToListDataType(input)
    else: return baseDataTypeToListDataType(input)


# Base Data Type <-> List Data Type
def listDataTypeToBaseDataType(dataType):
    listIdName = toIdName(dataType)
    baseIdName = listIdNameToBaseIdName(listIdName)
    baseDataType = toDataType(baseIdName)
    return baseDataType

def baseDataTypeToListDataType(dataType):
    baseIdName = toIdName(dataType)
    listIdName = baseIdNameToListIdName(baseIdName)
    listDataType = toDataType(listIdName)
    return listDataType

# Base Id Name <-> List Data Type
def listDataTypeToBaseIdName(dataType):
    listIdName = toIdName(dataType)
    baseIdName = listIdNameToBaseIdName(listIdName)
    return baseIdName

def baseIdNameToListDataType(idName):
    listIdName = baseDataTypeToListIdName(idName)
    listDataType = toDataType(listIdName)
    return listDataType

# Base Data Type <-> List Id Name
def listIdNameToBaseDataType(idName):
    baseIdName = listIdNameToBaseIdName(idName)
    baseDataType = toDataType(baseIdName)
    return baseDataType

def baseDataTypeToListIdName(dataType):
    baseIdName = toIdName(dataType)
    listIdName = baseIdNameToListIdName(baseIdName)
    return listIdName

# Base Id Name <-> List Id Name
def listIdNameToBaseIdName(idName):
    for listChain in listChains:
        if idName in listChain:
            index = listChain.index(idName)
            if index == 0: return None
            else: return listChain[index - 1]

def baseIdNameToListIdName(idName):
    for listChain in listChains:
        if idName in listChain:
            index = listChain.index(idName)
            if index == len(listChain) - 1: return None
            return listChain[index + 1]
    return None

# Data Type <-> Id Name
def toIdName(input):
    if isIdName(input): return input
    for subClass in getSocketClasses():
        if getattr(subClass, "dataType") == input: return subClass.bl_idname
    return None

def toDataType(input):
    if not isIdName(input): return input
    cls = getattr(bpy.types, input)
    return cls.dataType

def isIdName(name):
    return name.startswith("mn_")



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
    from .. base_types.socket import AnimationNodeSocket
    return AnimationNodeSocket.__subclasses__()
