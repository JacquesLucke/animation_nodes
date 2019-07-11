import bpy
from .. data_structures import Layer
from .. base_types import AnimationNodeSocket, PythonListSocket

class LayerSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_LayerSocket"
    bl_label = "Layer Socket"
    dataType = "Layer"
    drawColor = (0.85, 0.1, 0.35, 1)
    storable = True
    comparable = False

    @classmethod
    def getDefaultValue(cls):
        return Layer()

    @classmethod
    def getCopyExpression(cls):
        return "value.copy()"

    @classmethod
    def correctValue(cls, value):
        if isinstance(value, Layer):
            return value, 0
        return cls.getDefaultValue(), 2


class LayerListSocket(bpy.types.NodeSocket, PythonListSocket):
    bl_idname = "an_LayerListSocket"
    bl_label = "Layer List Socket"
    dataType = "Layer List"
    baseType = LayerSocket
    drawColor = (0.7, 0.1, 0.35, 0.5)
    storable = True
    comparable = False

    @classmethod
    def getCopyExpression(cls):
        return "[element.copy() for element in value]"

    @classmethod
    def correctValue(cls, value):
        if isinstance(value, list):
            if all(isinstance(element, Layer) for element in value):
                return value, 0
        return cls.getDefaultValue(), 2
