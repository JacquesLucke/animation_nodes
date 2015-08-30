import bpy
from .. base_types.socket import AnimationNodeSocket

class ObjectListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_ObjectListSocket"
    bl_label = "Object List Socket"
    dataType = "Object List"
    allowedInputTypes = ["Object List"]
    drawColor = (0, 0, 0, 0.4)

    def getValue(self):
        return []

    def getValueCode(self):
        return "[]"

    def getCopyStatement(self):
        return "value[:]"
