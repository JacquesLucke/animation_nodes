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

    @classmethod
    def getCopyExpression(cls):
        return "value[:]"


class PolygonIndicesListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_PolygonIndicesListSocket"
    bl_label = "Polygon Indices List Socket"
    dataType = "Polygon Indices List"
    baseDataType = "Polygon Indices"
    allowedInputTypes = ["Polygon Indices List"]
    drawColor = (0.6, 0.3, 0.8, 0.5)
    storable = True
    comparable = False

    def getValueCode(self):
        return "[]"

    @classmethod
    def getCopyExpression(cls):
        return "[polygonIndices[:] for polygonIndices in value]"
