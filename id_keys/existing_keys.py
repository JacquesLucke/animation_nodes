import bpy
from collections import namedtuple
from .. utils.handlers import eventHandler
from .. utils.operators import makeOperator
from . data_types import dataTypeIdentifiers

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
            if key.startswith("AN*"): collectedKeys.add(key)

    realKeys = filterRealIDKeys(collectedKeys)
    realKeys.update(getDefaultIDKeys())
    return realKeys

IDKey = namedtuple("IDKey", ["type", "name"])
def getDefaultIDKeys():
    return [IDKey("Transforms", "Initial Transforms")]

def filterRealIDKeys(keys):
    realKeys = set()
    for key in keys:
        parts = key.split("*")
        if len(parts) == 3:
            if parts[1] in dataTypeIdentifiers:
                realKeys.add(IDKey(parts[1], parts[2]))
        elif len(parts) == 4:
            if parts[1] in dataTypeIdentifiers:
                realKeys.add(IDKey(parts[1], parts[3]))
    return realKeys
