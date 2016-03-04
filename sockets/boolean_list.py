import bpy
from .. base_types.socket import AnimationNodeSocket

class BooleanListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_BooleanListSocket"
    bl_label = "Boolean List Socket"
    dataType = "Boolean List"
    allowedInputTypes = ["Boolean List"]
    drawColor = (0.7, 0.7, 0.4, 0.5)
    storable = True
    hashable = False

    def getValueCode(self):
        return "[]"

    def getCopyExpression(self):
        return "value[:]"
