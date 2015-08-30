import bpy
from .. base_types.socket import AnimationNodeSocket

class PolygonIndicesSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_PolygonIndicesSocket"
    bl_label = "Polygon Indices Socket"
    dataType = "Polygon Indices"
    allowedInputTypes = ["Polygon Indices"]
    drawColor = (0.5, 0.8, 0.4, 1)

    def getValueCode(self):
        return "(0, 1, 2)"

    def getCopyStatement(self):
        return "value[:]"
