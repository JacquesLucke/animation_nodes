import bpy
from .. base_types.socket import AnimationNodeSocket

class IntegerListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_IntegerListSocket"
    bl_label = "Integer List Socket"
    dataType = "Integer List"
    allowedInputTypes = ["Integer List"]
    drawColor = (0.2, 0.0, 0.9, 1.0)

    def getValue(self):
        return []

    def getValueCode(self):
        return "[]"

    def getCopyStatement(self):
        return "value[:]"
