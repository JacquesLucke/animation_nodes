'''
The ID Key system allows to store custom data inside of ID objects (Objects, ...).
Therefor it builds upon the normal ID properties Blender provides.

The key (properties name always has a specific form):
AN * Data Type * Property Name * Subproperty Name

The total length of this string is limited to 63 characters.
The individual parts are separated with ' * '
'''

import bpy
from bpy.props import *
from collections import namedtuple
from mathutils import Vector, Euler
from bpy.app.handlers import persistent
from . utils.operators import makeOperator

def doesIDKeyExist(object, dataType, propertyName):
    typeClass = dataTypeByIdentifier.get(dataType, None)
    return typeClass.exists(object, propertyName) if typeClass else False

def getIDKeyData(object, dataType, propertyName):
    typeClass = dataTypeByIdentifier.get(dataType, None)
    return typeClass.get(object, propertyName) if typeClass else None

def setIDKeyData(object, dataType, propertyName, data):
    typeClass = dataTypeByIdentifier.get(dataType, None)
    if typeClass is not None:
        typeClass.set(object, propertyName, data)


idKeysInFile = []

@makeOperator("an.update_id_keys_list", "Update ID Key List")
def updateIdKeysList():
    idKeysInFile.clear()
    idKeysInFile.extend(findIDKeysInCurrentFile())

def getAllIDKeys():
    return idKeysInFile

def findIDKeysInCurrentFile():
    collectedKeys = set()
    for object in bpy.data.objects:
        for key in object.keys():
            if key.startswith("AN * "): collectedKeys.add(key)

    return filterRealIDKeys(collectedKeys)

def getIDKeysOfObject(object):
    collectedKeys = set()
    for key in object.keys():
        if key.startswith("AN * "): collectedKeys.add(key)

    return filterRealIDKeys(collectedKeys)

IDKey = namedtuple("IDKey", ["type", "name"])
def filterRealIDKeys(keys):
    realKeys = set()
    for key in keys:
        parts = key.split(" * ")
        if len(parts) != 4: continue
        if parts[1] not in dataTypeIdentifiers: continue
        realKeys.add(IDKey(parts[1], parts[2]))
    return realKeys



# ID Key Data Types
#######################################

class IDKeyDataType:
    pass

class TransformDataType(IDKeyDataType):
    identifier = "Transforms"
    subproperties = ("Location", "Rotation", "Scale")

    @classmethod
    def create(cls, object, name):
        cls.set(object, name, ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (1.0, 1.0, 1.0)))

    @classmethod
    def remove(cls, object, name):
        for key in cls.getPropertyKeys(name):
            if key in object: del object[key]

    @classmethod
    def exists(cls, object, name):
        return all(hasIDProperty(object, key) for key in cls.getPropertyKeys(name))

    @classmethod
    def set(cls, object, name, data):
        for i, key in enumerate(cls.getPropertyKeys(name)):
            object[key] = data[i]

    @classmethod
    def get(cls, object, name):
        keys = cls.getPropertyKeys(name)
        return [Vector(getIDProperty(object, keys[0], (0.0, 0.0, 0.0))),
                Euler(getIDProperty(object, keys[1], (0.0, 0.0, 0.0))),
                Vector(getIDProperty(object, keys[2], (1.0, 1.0, 1.0))) ]

    @classmethod
    def getPropertyKeys(cls, name):
        return list(joinMultiple(cls.identifier, name, cls.subproperties))

class SingleValueDataType:
    identifier = None
    default = None

    @classmethod
    def create(cls, object, name):
        cls.set(object, name, cls.default)

    @classmethod
    def remove(cls, object, name):
        key = cls.getPropertyKey(name)
        if key in object: del object[key]

    @classmethod
    def exists(cls, object, name):
        return hasIDProperty(object, cls.getPropertyKey(name))

    @classmethod
    def set(cls, object, name, data):
        object[cls.getPropertyKey(name)] = data

    @classmethod
    def get(cls, object, name):
        return getIDProperty(object, cls.getPropertyKey(name), cls.default)

    @classmethod
    def getPropertyKey(cls, name):
        return joinSingle(cls.identifier, name)

class StringDataType(SingleValueDataType, IDKeyDataType):
    identifier = "String"
    default = ""

class IntegerDataType(SingleValueDataType, IDKeyDataType):
    identifier = "Integer"
    default = 0

class FloatDataType(SingleValueDataType, IDKeyDataType):
    identifier = "Float"
    default = 0.0

dataTypeByIdentifier = { dataType.identifier : dataType
     for dataType in IDKeyDataType.__subclasses__()
     if dataType.identifier is not None }

dataTypeIdentifiers = dataTypeByIdentifier.keys()



# Misc
###################################

def joinSingle(dataType, propertyName):
    return "AN * {} * {} * ".format(dataType, propertyName)

def joinMultiple(dataType, propertyName, subproperties):
    prefix = joinSingle(dataType, propertyName)
    for subproperty in subproperties:
        yield prefix + subproperty

def getIDProperty(object, name, default):
    return getattr(object, toPath(name), default)

def hasIDProperty(object, name):
    return hasattr(object, toPath(name))

def toPath(name):
    return '["{}"]'.format(name)



# Register
################################

class IDKeyProperties(bpy.types.PropertyGroup):
    bl_idname = "an_id_key_properties"

    def _getIDKeyData(self, dataType, propertyName):
        return getIDKeyData(self.id_data, dataType, propertyName)

    def _setIDKeyData(self, dataType, propertyName, data):
        return setIDKeyData(self.id_data, dataType, propertyName, data)

    def _doesIDKeyExist(self, dataType, propertyName):
        return doesIDKeyExist(self.id_data, dataType,propertyName)

    def _getAllIDKeys(self):
        return getIDKeysOfObject(self.id_data)

    get = _getIDKeyData
    set = _setIDKeyData
    exists = _doesIDKeyExist
    getAll = _getAllIDKeys

@persistent
def fileLoad(scene):
    updateIdKeysList()

def register():
    bpy.types.ID.id_keys = PointerProperty(type = IDKeyProperties)
    bpy.app.handlers.load_post.append(fileLoad)

def unregister():
    del bpy.types.ID.id_keys
    bpy.app.handlers.load_post.remove(fileLoad)
