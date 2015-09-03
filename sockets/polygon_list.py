import bpy
from .. base_types.socket import AnimationNodeSocket

class PolygonListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_PolygonListSocket"
    bl_label = "Polygon List Socket"
    dataType = "Polygon List"
    allowedInputTypes = ["Polygon List"]
    drawColor = (0.25, 0.55, 0.23, 1)

    def getValueCode(self):
        return "[]"

    def getCopyExpression(self):
        return "[element.copy() for element in value]"
