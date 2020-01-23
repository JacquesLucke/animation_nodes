import bpy

def getActiveDepsgraph():
    return bpy.context.evaluated_depsgraph_get()

def getEvaluatedID(idObject):
    return idObject.evaluated_get(getActiveDepsgraph())
