import bpy
from .. base_types.socket import AnimationNodeSocket

class FontListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_FontListSocket"
    bl_label = "Font List Socket"
    dataType = "Font List"
    allowedInputTypes = ["Font List"]
    drawColor = (0.444, 0.444, 0, 0.5)
    storable = False
    comparable = False

    def getValueCode(self):
        return "[]"

    def getCopyExpression(self):
        return "value[:]"
