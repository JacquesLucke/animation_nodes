import bpy
from functools import lru_cache
from .. utils.enum_items import enumItemsFromList

listChains = [
    ["an_FloatSocket",              "an_FloatListSocket"],
    ["an_IntegerSocket",            "an_IntegerListSocket"],
    ["an_VectorSocket",             "an_VectorListSocket"],
    ["an_ColorSocket",              "an_ColorListSocket"],
    ["an_ObjectSocket",             "an_ObjectListSocket"],
    ["an_StringSocket",             "an_StringListSocket"],
    ["an_EdgeIndicesSocket",        "an_EdgeIndicesListSocket"],
    ["an_PolygonIndicesSocket",     "an_PolygonIndicesListSocket"],
    ["an_ParticleSocket",           "an_ParticleListSocket"],
    ["an_ParticleSystemSocket",     "an_ParticleSystemListSocket"],
    ["an_SplineSocket",             "an_SplineListSocket"],
    ["an_MatrixSocket",             "an_MatrixListSocket"],
    ["an_MeshDataSocket",           "an_MeshDataListSocket"],
    ["an_SequenceSocket",           "an_SequenceListSocket"],
    ["an_PolygonSocket",            "an_PolygonListSocket"],
    ["an_VertexSocket",             "an_VertexListSocket"],
    ["an_GenericSocket",            "an_GenericListSocket"],
    ["an_FCurveSocket",             "an_FCurveListSocket"],
    ["an_ObjectGroupSocket",        "an_ObjectGroupListSocket"],
    ["an_EulerSocket",              "an_EulerListSocket"],
    ["an_QuaternionSocket",         "an_QuaternionListSocket"],
    ["an_TextBlockSocket",          "an_TextBlockListSocket"],
    ["an_SceneSocket",              "an_SceneListSocket"],
    ["an_InterpolationSocket",      "an_InterpolationListSocket"],
    ["an_FontSocket",               "an_FontListSocket"],
    ["an_ShapeKeySocket",           "an_ShapeKeyListSocket"],
    ["an_BooleanSocket",            "an_BooleanListSocket"] ]

limitedListTypes = {
    "an_IntegerListSocket" : ("an_EdgeIndicesSocket", "an_PolygonIndicesSocket") }


def returnNoneOnFailure(function):
    def wrapper(*args, **kwargs):
        try: return function(*args, **kwargs)
        except: return None
    return wrapper


# Check if list or base socket exists
@returnNoneOnFailure
def isList(input):
    if not isIdName(input): input = toIdName(input)
    return listIdNameToBaseIdName(input) is not None

@returnNoneOnFailure
def isBase(input):
    if not isIdName(input): input = toIdName(input)
    return baseDataTypeToListIdName(input) is not None


# to Base
@returnNoneOnFailure
def toBaseIdName(input):
    if isIdName(input): return listIdNameToBaseIdName(input)
    else: return listDataTypeToBaseIdName(input)

@returnNoneOnFailure
def toBaseDataType(input):
    if isIdName(input): return listIdNameToBaseDataType(input)
    else: return listDataTypeToBaseDataType(input)

# to List
@returnNoneOnFailure
def toListIdName(input):
    if isIdName(input): return baseIdNameToListIdName(input)
    else: return baseDataTypeToListIdName(input)

@returnNoneOnFailure
def toListDataType(input):
    if isIdName(input): return baseIdNameToListDataType(input)
    else: return baseDataTypeToListDataType(input)

def isComparable(input):
    if not isIdName(input): input = toIdName(input)
    return getSocketClassFromIdName(input).comparable


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

def isLimitedList(idName):
    for limitedLists in limitedListTypes.values():
        if idName in limitedLists: return True
    return False

def toGeneralListIdName(limitedListIdName):
    for generalIdName, limitedLists in limitedListTypes.items():
        if limitedListIdName in limitedLists: return generalIdName


def getSocketClassFromIdName(idName):
    for cls in getSocketClasses():
        if cls.bl_idname == idName: return cls
    return None


def getListDataTypeItemsCallback(self, context):
    return getListDataTypeItems()

def getBaseDataTypeItemsCallback(self, context):
    return getBaseDataTypeItems()

def getListDataTypeItems():
    return enumItemsFromList(getListDataTypes())

def getBaseDataTypeItems():
    return enumItemsFromList(getBaseDataTypes())

def getDataTypeItems(skipInternalTypes = False):
    return enumItemsFromList(getDataTypes(skipInternalTypes))

def getListDataTypes():
    return [toDataType(idName) for idName in getListIdNames()]

def getBaseDataTypes():
    return [toDataType(idName) for idName in getBaseIdNames()]

def getDataTypes(skipInternalTypes = False):
    if skipInternalTypes:
        return [socketClass.dataType for socketClass in getSocketClasses() if socketClass.dataType != "Node Control"]
    else:
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
    return name.startswith("an_")
