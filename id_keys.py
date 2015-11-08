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
from . utils.handlers import eventHandler
from . utils.operators import makeOperator

def doesIDKeyExist(object, dataType, propertyName):
    typeClass = dataTypeByIdentifier.get(dataType, None)
    return typeClass.exists(object, propertyName) if typeClass else False

def createIDKey(object, dataType, propertyName):
    typeClass = dataTypeByIdentifier.get(dataType, None)
    if typeClass is not None:
        typeClass.create(object, propertyName)

def getIDKeyData(object, dataType, propertyName):
    typeClass = dataTypeByIdentifier.get(dataType, None)
    return typeClass.get(object, propertyName) if typeClass else None

def setIDKeyData(object, dataType, propertyName, data):
    typeClass = dataTypeByIdentifier.get(dataType, None)
    if typeClass is not None:
        typeClass.set(object, propertyName, data)

def removeIDKey(object, dataType, propertyName):
    typeClass = dataTypeByIdentifier.get(dataType, None)
    if typeClass is not None:
        typeClass.remove(object, propertyName)

def drawIDKeyProperty(layout, object, dataType, propertyName):
    typeClass = dataTypeByIdentifier.get(dataType, None)
    if typeClass is None:
        layout.label("Data Type does not exist", icon = "ERROR")
        return
    if typeClass.exists(object, propertyName):
        if hasattr(typeClass, "drawProperty"):
            typeClass.drawProperty(layout, object, propertyName)
    else:
        layout.label("ID Key does not exist yet", icon = "INFO")

def drawIDKeyExtras(layout, object, dataType, propertyName):
    typeClass = dataTypeByIdentifier.get(dataType, None)
    if hasattr(typeClass, "drawExtras"):
        typeClass.drawExtras(layout, object, propertyName)

idKeysInFile = []

@eventHandler("FILE_LOAD_POST")
@eventHandler("ADDON_LOAD_POST")
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

    realKeys = filterRealIDKeys(collectedKeys)
    realKeys.update(getDefaultIDKeys())
    return realKeys

IDKey = namedtuple("IDKey", ["type", "name"])
def getDefaultIDKeys():
    return [ IDKey("Transforms", "Initial Transforms") ]

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
    def drawProperty(cls, layout, object, name):
        keys = cls.getPropertyKeys(name)
        row = layout.row()

        for i, label in enumerate(["Location", "Rotation", "Scale"]):
            col = row.column(align = True)
            col.label(label)
            col.prop(object, toPath(keys[i]), text = "")

    @classmethod
    def drawExtras(cls, layout, object, name):
        props = layout.operator("an.id_key_from_current_transforms")
        props.name = name

    @classmethod
    def getPropertyKeys(cls, name):
        return list(joinMultiple(cls.identifier, name, cls.subproperties))

@makeOperator("an.id_key_from_current_transforms", "From Current Transforms", arguments = ["String"])
def idKeyFromCurrentTransforms(name):
    for object in bpy.context.selected_objects:
        object.id_keys.set("Transforms", name, (object.location, object.rotation_euler, object.scale))


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

    @classmethod
    def drawProperty(cls, layout, object, name):
        layout.prop(object, toPath(cls.getPropertyKey(name)), text = "")

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

    def _drawProperty(self, layout, dataType, propertyName):
        drawIDKeyProperty(layout, self.id_data, dataType, propertyName)

    def _drawExtras(self, layout, dataType, propertyName):
        drawIDKeyExtras(layout, self.id_data, dataType, propertyName)

    def _createIDKey(self, dataType, propertyName):
        createIDKey(self.id_data, dataType, propertyName)

    def _removeIDKey(self, dataType, propertyName):
        removeIDKey(self.id_data, dataType, propertyName)

    get = _getIDKeyData
    set = _setIDKeyData
    create = _createIDKey
    remove = _removeIDKey
    exists = _doesIDKeyExist
    drawProperty = _drawProperty
    drawExtras = _drawExtras

def register():
    bpy.types.ID.id_keys = PointerProperty(name = "ID Keys", type = IDKeyProperties)

def unregister():
    del bpy.types.ID.id_keys
