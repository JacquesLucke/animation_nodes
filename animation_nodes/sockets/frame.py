import bpy
from .. data_structures import Frame
from .. base_types import AnimationNodeSocket, PythonListSocket

class FrameSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_FrameSocket"
    bl_label = "Frame Socket"
    dataType = "Frame"
    drawColor = (0.69, 0.001, 0.01, 1)
    storable = True
    comparable = False

    @classmethod
    def getDefaultValue(cls):
        return Frame()

    @classmethod
    def getCopyExpression(cls):
        return "value.copy()"

    @classmethod
    def correctValue(cls, value):
        if isinstance(value, Frame):
            return value, 0
        return cls.getDefaultValue(), 2


class FrameListSocket(bpy.types.NodeSocket, PythonListSocket):
    bl_idname = "an_FrameListSocket"
    bl_label = "Frame List Socket"
    dataType = "Frame List"
    baseType = FrameSocket
    drawColor = (0.69, 0.001, 0.01, 0.5)
    storable = True
    comparable = False

    @classmethod
    def getCopyExpression(cls):
        return "[element.copy() for element in value]"

    @classmethod
    def correctValue(cls, value):
        if isinstance(value, list):
            if all(isinstance(element, Frame) for element in value):
                return value, 0
        return cls.getDefaultValue(), 2
