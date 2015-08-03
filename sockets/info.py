import bpy
from functools import lru_cache
from .. utils.enum_items import enumItemsFromList

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
@lru_cache(maxsize = None)
def listIdNameToBaseIdName(idName):
    for listChain in listChains:
        if idName in listChain:
            index = listChain.index(idName)
            if index == 0: return None
            else: return listChain[index - 1]

@lru_cache(maxsize = None)
def baseIdNameToListIdName(idName):
    for listChain in listChains:
        if idName in listChain:
            index = listChain.index(idName)
            if index == len(listChain) - 1: return None
            return listChain[index + 1]
    return None


def getSocketClassFromIdName(idName):
    for cls in getSocketClasses():
        if cls.bl_idname == idName: return cls
    return None


@enumItemsFromList
def getListDataTypeItems(self, context):
    return getListDataTypes()

@enumItemsFromList
def getBaseDataTypeItems(self, context):
    return getBaseDataTypes()      

@enumItemsFromList
def getDataTypeItems(self, context):
    return getDataTypes()

def getListDataTypes():
    return [toDataType(idName) for idName in getListIdNames()]

def getBaseDataTypes():
    return [toDataType(idName) for idName in getBaseIdNames()]

def getDataTypes():
    return [socketClass.dataType for socketClass in getSocketClasses()]


def getBaseIdNames():
    idNames = []
    for listChain in listChains:
        idNames.extend(listChain[:-1])
    return idNames

def getListIdNames():
    types = []
    for listChain in listChains:
        for i, type in enumerate(listChain):
            if i > 0:
                types.append(type)
    return types


# Data Type <-> Id Name
@lru_cache(maxsize = None)
def toIdName(input):
    if isIdName(input): return input
    for subClass in getSocketClasses():
        if getattr(subClass, "dataType") == input: return subClass.bl_idname
    return None

@lru_cache(maxsize = None)
def toDataType(input):
    if not isIdName(input): return input
    cls = getattr(bpy.types, input)
    return cls.dataType

def getSocketClasses():
    from .. base_types.socket import AnimationNodeSocket
    return AnimationNodeSocket.__subclasses__()

def isIdName(name):
    return name.startswith("mn_")
