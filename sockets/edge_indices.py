import bpy
from .. base_types.socket import AnimationNodeSocket

class EdgeIndicesSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_EdgeIndicesSocket"
    bl_label = "Edge Indices Socket"
    dataType = "Edge Indices"
    allowedInputTypes = ["Edge Indices"]
    drawColor = (0.4, 0.6, 0.6, 1)
    comparable = True
    storable = True

    def getValueCode(self):
        return "(0, 1)"

    @classmethod
    def getCopyExpression(cls):
        return "value[:]"


class EdgeIndicesListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_EdgeIndicesListSocket"
    bl_label = "Edge Indices List Socket"
    dataType = "Edge Indices List"
    baseDataType = "Edge Indices"
    allowedInputTypes = ["Edge Indices List"]
    drawColor = (0.4, 0.6, 0.6, 0.5)
    storable = True
    comparable = False

    def getValueCode(self):
        return "[]"

    @classmethod
    def getCopyExpression(cls):
        return "[edgeIndices[:] for edgeIndices in value]"
