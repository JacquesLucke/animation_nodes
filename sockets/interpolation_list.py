import bpy
from .. base_types.socket import AnimationNodeSocket

class InterpolationListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_InterpolationListSocket"
    bl_label = "Interpolation List Socket"
    dataType = "Interpolation List"
    allowedInputTypes = ["Interpolation List"]
    drawColor = (0.7, 0.4, 0.3, 0.5)
    storable = False
    hashable = False

    def getValueCode(self):
        return "[]"

    def getCopyExpression(self):
        return "value[:]"
