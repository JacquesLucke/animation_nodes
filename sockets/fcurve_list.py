import bpy
from .. base_types.socket import AnimationNodeSocket

class FCurveListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_FCurveListSocket"
    bl_label = "FCurve List Socket"
    dataType = "FCurve List"
    allowedInputTypes = ["FCurve List"]
    drawColor = (0.2, 0.26, 0.19, 0.5)

    def getValueCode(self):
        return "[]"

    def getCopyExpression(self):
        return "value[:]"
