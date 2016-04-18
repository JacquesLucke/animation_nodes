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

    @classmethod
    def getDefaultValue(cls):
        return (0, 1)

    @classmethod
    def getDefaultValueCode(cls):
        return "(0, 1)"

    @classmethod
    def getCopyExpression(cls):
        return "value[:]"

    @classmethod
    def correctValue(cls, value):
        if isEdge(value): return value, 0
        else: return cls.getDefaultValue(), 2


class EdgeIndicesListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_EdgeIndicesListSocket"
    bl_label = "Edge Indices List Socket"
    dataType = "Edge Indices List"
    baseDataType = "Edge Indices"
    allowedInputTypes = ["Edge Indices List"]
    drawColor = (0.4, 0.6, 0.6, 0.5)
    storable = True
    comparable = False

    @classmethod
    def getDefaultValue(cls):
        return []

    @classmethod
    def getDefaultValueCode(cls):
        return "[]"

    @classmethod
    def getCopyExpression(cls):
        return "[edgeIndices[:] for edgeIndices in value]"

    @classmethod
    def correctValue(cls, value):
        if isinstance(value, list):
            if all(isEdge(element) for element in value):
                return value, 0
        return cls.getDefaultValue(), 2


def isEdge(value):
    if isinstance(value, tuple):
        return len(value) == 2 and all(isinstance(element, int) for element in value)
    return False
