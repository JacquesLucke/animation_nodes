import bpy
from collections import namedtuple
from .. tree_info import getNodesByType
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
    foundKeys = set()
    foundKeys.update(getIDKeysOfNodes())
    foundKeys.update(getIDKeysOnObjects())

    # default keys should stay in order
    allKeys = list()
    allKeys.extend(getDefaultIDKeys())
    for key in foundKeys:
        if key not in allKeys:
            allKeys.append(key)
    return allKeys

IDKey = namedtuple("IDKey", ["type", "name"])
def getDefaultIDKeys():
    return [IDKey("Transforms", "Initial Transforms")]

def getIDKeysOfNodes():
    idKeys = set()
    for node in getNodesByType("an_ObjectIDKeyNode"):
        if node.keyName != "":
            idKeys.add(IDKey(node.keyDataType, node.keyName))
    return idKeys

def getIDKeysOnObjects():
    possibleKeys = set()
    for object in bpy.data.objects:
        for key in object.keys():
            if key.startswith("AN*"): possibleKeys.add(key)
    return filterRealIDKeys(possibleKeys)

def filterRealIDKeys(possibleKeys):
    realIDKeys = set()
    for key in possibleKeys:
        parts = key.split("*")
        if len(parts) == 3:
            if parts[1] in dataTypeIdentifiers:
                realIDKeys.add(IDKey(parts[1], parts[2]))
        elif len(parts) == 4:
            if parts[1] in dataTypeIdentifiers:
                realIDKeys.add(IDKey(parts[1], parts[3]))
    return realIDKeys
