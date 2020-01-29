import bpy
from .. data_structures import GPStroke
from .. base_types import AnimationNodeSocket, PythonListSocket

class GPStrokeSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_GPStrokeSocket"
    bl_label = "GPStroke Socket"
    dataType = "GPStroke"
    drawColor = (0.85, 0.35, 0.0, 1)
    storable = True
    comparable = False

    @classmethod
    def getDefaultValue(cls):
        return GPStroke()

    @classmethod
    def getCopyExpression(cls):
        return "value.copy()"

    @classmethod
    def correctValue(cls, value):
        if isinstance(value, GPStroke):
            return value, 0
        return cls.getDefaultValue(), 2


class GPStrokeListSocket(bpy.types.NodeSocket, PythonListSocket):
    bl_idname = "an_GPStrokeListSocket"
    bl_label = "GPStroke List Socket"
    dataType = "GPStroke List"
    baseType = GPStrokeSocket
    drawColor = (0.85, 0.35, 0.0, 0.5)
    storable = True
    comparable = False

    @classmethod
    def getCopyExpression(cls):
        return "[element.copy() for element in value]"

    @classmethod
    def correctValue(cls, value):
        if isinstance(value, list):
            if all(isinstance(element, GPStroke) for element in value):
                return value, 0
        return cls.getDefaultValue(), 2
