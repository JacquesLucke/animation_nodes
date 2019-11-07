import bpy

def getActiveDepsgraph():
    return bpy.context.evaluated_depsgraph_get()

def getEvaluatedID(id):
    return id.evaluated_get(getActiveDepsgraph())
