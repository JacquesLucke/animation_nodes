import bpy
from .. data_structures import GPLayer
from .. base_types import AnimationNodeSocket, PythonListSocket

class GPLayerSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_GPLayerSocket"
    bl_label = "GPLayer Socket"
    dataType = "GPLayer"
    drawColor = (0.85, 0.1, 0.35, 1)
    storable = True
    comparable = False

    @classmethod
    def getDefaultValue(cls):
        return GPLayer()

    @classmethod
    def getCopyExpression(cls):
        return "value.copy()"

    @classmethod
    def correctValue(cls, value):
        if isinstance(value, GPLayer):
            return value, 0
        return cls.getDefaultValue(), 2


class GPLayerListSocket(bpy.types.NodeSocket, PythonListSocket):
    bl_idname = "an_GPLayerListSocket"
    bl_label = "GPLayer List Socket"
    dataType = "GPLayer List"
    baseType = GPLayerSocket
    drawColor = (0.7, 0.1, 0.35, 0.5)
    storable = True
    comparable = False

    @classmethod
    def getCopyExpression(cls):
        return "[element.copy() for element in value]"

    @classmethod
    def correctValue(cls, value):
        if isinstance(value, list):
            if all(isinstance(element, GPLayer) for element in value):
                return value, 0
        return cls.getDefaultValue(), 2
