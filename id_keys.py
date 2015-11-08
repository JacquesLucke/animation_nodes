'''
The ID Key system allows to store custom data inside of ID objects (Objects, ...).
Therefor it builds upon the normal ID properties Blender provides.

The key (properties name always has a specific form):
AN * Data Type * Property Name * Subproperty Name

The total length of this string is limited to 63 characters.
The individual parts are separated with ' * '
'''

import bpy
from collections import namedtuple
from mathutils import Vector, Euler

def getIDKeyInfo(object, dataType, propertyName):
    typeClass = dataTypeByIdentifier.get(dataType, None)
    if typeClass is None: return None, False
    return typeClass.get(object, propertyName), typeClass.exists(object, propertyName)

def setIDKeyData(object, dataType, propertyName, data):
    typeClass = dataTypeByIdentifier.get(dataType, None)
    if typeClass is not None:
        typeClass.set(object, propertyName, data)

def getIDKeysInCurrentFile():
    collectedKeys = set()
    for object in bpy.data.objects:
        for key in object.keys():
            if key.startswith("AN * "): collectedKeys.add(key)

    idKeys = set()
    IDKey = namedtuple("IDKey", ["type", "name"])
    dataTypeIdentifiers = dataTypeByIdentifier.keys()
    for key in collectedKeys:
        parts = key.split(" * ")
        if len(parts) != 4: continue
        if parts[1] not in dataTypeIdentifiers: continue
        idKeys.add(IDKey(parts[1], parts[2]))

    return list(idKeys)



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

def register():
    bpy.types.ID.getIDKeyInfo = getIDKeyInfo
    bpy.types.ID.setIDKeyData = setIDKeyData

def unregister():
    del bpy.types.ID.getIDKeyInfo
    del bpy.types.ID.setIDKeyData
