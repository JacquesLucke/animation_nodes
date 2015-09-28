import bpy
from .. base_types.socket import AnimationNodeSocket

class ColorListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_ColorListSocket"
    bl_label = "Color List Socket"
    dataType = "Color List"
    allowedInputTypes = ["Color List"]
    drawColor = (0.8, 0.8, 0.2, 0.5)

    def getValueCode(self):
        return "[]"

    def getCopyExpression(self):
        return "[element[:] for element in value]"
