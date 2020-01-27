import bpy
from .. import events

def getActiveDepsgraph():
    if events.evaluatedDepsgraph: return events.evaluatedDepsgraph
    return bpy.context.evaluated_depsgraph_get()

def getEvaluatedID(idObject):
    return idObject.evaluated_get(getActiveDepsgraph())
