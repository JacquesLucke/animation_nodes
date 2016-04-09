import bpy
from collections import defaultdict
from .. utils.enum_items import enumItemsFromList

class SocketInfo:
    def __init__(self):
        self.reset()

    def reset(self):
        self.idNames = set()
        self.dataTypes = set()

        self.classByType = dict()
        self.typeConversion = dict()

        self.baseIdName = dict()
        self.listIdName = dict()
        self.baseDataType = dict()
        self.listDataType = dict()

        self.baseDataTypes = set()
        self.listDataTypes = set()

    def update(self, socketClasses, listChains):
        self.reset()

        for socketClass in socketClasses:
            self.insertSocket(socketClass)

        for chain in listChains:
            for baseIdName, listIdName in zip(chain[:-1], chain[1:]):
                self.insertBaseListConnection(baseIdName, listIdName)

    def insertSocket(self, socketClass):
        idName = socketClass.bl_idname
        dataType = socketClass.dataType

        self.idNames.add(idName)
        self.dataTypes.add(dataType)

        self.classByType[idName] = socketClass
        self.classByType[dataType] = socketClass

        self.typeConversion[idName] = dataType
        self.typeConversion[dataType] = idName

    def insertBaseListConnection(self, baseIdName, listIdName):
        listDataType = self.typeConversion[listIdName]
        baseDataType = self.typeConversion[baseIdName]

        self.baseIdName[listIdName] = baseIdName
        self.baseIdName[listDataType] = baseIdName
        self.listIdName[baseIdName] = listIdName
        self.listIdName[baseDataType] = listIdName

        self.baseDataType[listIdName] = baseDataType
        self.baseDataType[listDataType] = baseDataType
        self.listDataType[baseIdName] = listDataType
        self.listDataType[baseDataType] = listDataType

        self.listDataTypes.add(listDataType)
        self.baseDataTypes.add(baseDataType)


_socketInfo = SocketInfo()

def updateSocketInfo():
    socketClasses = getSocketClasses()
    _socketInfo.update(socketClasses, listChains)

def getSocketClasses():
    from .. base_types.socket import AnimationNodeSocket
    return AnimationNodeSocket.__subclasses__()

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


def returnNoneOnFailure(function):
    def wrapper(*args, **kwargs):
        try: return function(*args, **kwargs)
        except: return None
    return wrapper

# Check if list or base socket exists
def isList(input):
    return input in _socketInfo.baseIdName

def isBase(input):
    return input in _socketInfo.listIdName

# to Base
@returnNoneOnFailure
def toBaseIdName(input):
    return _socketInfo.baseIdName[input]

@returnNoneOnFailure
def toBaseDataType(input):
    return _socketInfo.baseDataType[input]

# to List
@returnNoneOnFailure
def toListIdName(input):
    return _socketInfo.listIdName[input]

@returnNoneOnFailure
def toListDataType(input):
    return _socketInfo.listDataType[input]

# Data Type <-> Id Name
@returnNoneOnFailure
def toIdName(input):
    if isIdName(input): return input
    return _socketInfo.typeConversion[input]

@returnNoneOnFailure
def toDataType(input):
    if isIdName(input):
        return _socketInfo.typeConversion[input]
    return input

def isIdName(name):
    return name in _socketInfo.idNames


@returnNoneOnFailure
def isComparable(input):
    return _socketInfo.classByType[input].comparable


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
    return list(_socketInfo.listDataTypes)

def getBaseDataTypes():
    return list(_socketInfo.baseDataTypes)

def getDataTypes(skipInternalTypes = False):
    internalTypes = {"Node Control"}
    if skipInternalTypes:
        return [dataType for dataType in _socketInfo.dataTypes if dataType not in internalTypes]
    else:
        return list(_socketInfo.dataTypes)
