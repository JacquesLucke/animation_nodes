import bpy
from .. data_structures import GPFrame
from .. base_types import AnimationNodeSocket, PythonListSocket

class GPFrameSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_GPFrameSocket"
    bl_label = "GPFrame Socket"
    dataType = "GPFrame"
    drawColor = (0.69, 0.001, 0.01, 1)
    storable = True
    comparable = False

    @classmethod
    def getDefaultValue(cls):
        return GPFrame()

    @classmethod
    def getCopyExpression(cls):
        return "value.copy()"

    @classmethod
    def correctValue(cls, value):
        if isinstance(value, GPFrame):
            return value, 0
        return cls.getDefaultValue(), 2


class GPFrameListSocket(bpy.types.NodeSocket, PythonListSocket):
    bl_idname = "an_GPFrameListSocket"
    bl_label = "GPFrame List Socket"
    dataType = "GPFrame List"
    baseType = GPFrameSocket
    drawColor = (0.69, 0.001, 0.01, 0.5)
    storable = True
    comparable = False

    @classmethod
    def getCopyExpression(cls):
        return "[element.copy() for element in value]"

    @classmethod
    def correctValue(cls, value):
        if isinstance(value, list):
            if all(isinstance(element, GPFrame) for element in value):
                return value, 0
        return cls.getDefaultValue(), 2
