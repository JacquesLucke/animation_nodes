import bpy
from .. data_structures import Stroke
from .. base_types import AnimationNodeSocket, PythonListSocket

class StrokeSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_StrokeSocket"
    bl_label = "Stroke Socket"
    dataType = "Stroke"
    drawColor = (0.85, 0.35, 0.0, 1)
    storable = True
    comparable = False

    @classmethod
    def getDefaultValue(cls):
        return Stroke()

    @classmethod
    def getCopyExpression(cls):
        return "value.copy()"

    @classmethod
    def correctValue(cls, value):
        if isinstance(value, Stroke):
            return value, 0
        return cls.getDefaultValue(), 2


class StrokeListSocket(bpy.types.NodeSocket, PythonListSocket):
    bl_idname = "an_StrokeListSocket"
    bl_label = "Stroke List Socket"
    dataType = "Stroke List"
    baseType = StrokeSocket
    drawColor = (0.85, 0.35, 0.0, 0.5)
    storable = True
    comparable = False

    @classmethod
    def getCopyExpression(cls):
        return "[element.copy() for element in value]"

    @classmethod
    def correctValue(cls, value):
        if isinstance(value, list):
            if all(isinstance(element, Stroke) for element in value):
                return value, 0
        return cls.getDefaultValue(), 2
