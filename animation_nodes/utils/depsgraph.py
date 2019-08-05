import bpy

def getActiveDepsgraph():
    return bpy.context.evaluated_depsgraph_get()

def getEvaluatedObject(object):
    return object.evaluated_get(getActiveDepsgraph())
