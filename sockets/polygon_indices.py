import bpy
from .. base_types.socket import AnimationNodeSocket

class PolygonIndicesSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_PolygonIndicesSocket"
    bl_label = "Polygon Indices Socket"
    dataType = "Polygon Indices"
    allowedInputTypes = ["Polygon Indices"]
    drawColor = (0.6, 0.3, 0.8, 1)
    comparable = True
    storable = True

    def getValueCode(self):
        return "(0, 1, 2)"

    def getCopyExpression(self):
        return "value[:]"
