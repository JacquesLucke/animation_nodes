import bpy
from .. base_types.socket import AnimationNodeSocket

class IntegerListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_IntegerListSocket"
    bl_label = "Integer List Socket"
    dataType = "Integer List"
    allowedInputTypes = ["Integer List"]
    drawColor = (0.3, 0.4, 1.0, 0.5)

    def getValueCode(self):
        return "[]"

    def getCopyExpression(self):
        return "value[:]"
