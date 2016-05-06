import bpy
from .. base_types.socket import AnimationNodeSocket, ListSocket

class PolygonIndicesSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_PolygonIndicesSocket"
    bl_label = "Polygon Indices Socket"
    dataType = "Polygon Indices"
    allowedInputTypes = ["Polygon Indices"]
    drawColor = (0.6, 0.3, 0.8, 1)
    comparable = True
    storable = True

    @classmethod
    def getDefaultValue(cls):
        return (0, 1, 2)

    @classmethod
    def getDefaultValueCode(cls):
        return "(0, 1, 2)"

    @classmethod
    def getCopyExpression(cls):
        return "value[:]"

    @classmethod
    def correctValue(cls, value):
        if isPolygon(value): return value, 0
        else: return cls.getDefaultValue(), 2


class PolygonIndicesListSocket(bpy.types.NodeSocket, AnimationNodeSocket, ListSocket):
    bl_idname = "an_PolygonIndicesListSocket"
    bl_label = "Polygon Indices List Socket"
    dataType = "Polygon Indices List"
    baseDataType = "Polygon Indices"
    allowedInputTypes = ["Polygon Indices List"]
    drawColor = (0.6, 0.3, 0.8, 0.5)
    storable = True
    comparable = False

    @classmethod
    def getCopyExpression(cls):
        return "[polygonIndices[:] for polygonIndices in value]"

    @classmethod
    def correctValue(cls, value):
        if isinstance(value, list):
            if all(isPolygon(element) for element in value):
                return value, 0
        return cls.getDefaultValue(), 2


def isPolygon(value):
    if isinstance(value, tuple):
        return len(value) >= 3 and all(isinstance(element, int) for element in value)
    return False
