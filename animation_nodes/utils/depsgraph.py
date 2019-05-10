import bpy

def getActiveDepsgraph():
    return bpy.context.depsgraph

def getEvaluatedObject(object):
    return getActiveDepsgraph().objects.get(object.name)
