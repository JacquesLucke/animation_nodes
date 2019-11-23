import bpy
from bpy.props import *
from .. events import propertyChanged
from .. data_structures import Color, ColorList
from .. base_types import AnimationNodeSocket, CListSocket

class ColorSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_ColorSocket"
    bl_label = "Color Socket"
    dataType = "Color"
    drawColor = (0.8, 0.8, 0.2, 1)
    storable = True
    comparable = False

    value: FloatVectorProperty(
        default = [0.5, 0.5, 0.5, 1.0], subtype = "COLOR", size = 4,
        soft_min = 0.0, soft_max = 1.0,
        update = propertyChanged)

    def drawProperty(self, layout, text, node):
        layout.prop(self, "value", text = text)

    def getValue(self):
        return Color(self.value)

    def setProperty(self, data):
        self.value = data

    def getProperty(self):
        return self.value[:]

    @classmethod
    def getDefaultValue(cls):
        return Color((0, 0, 0, 1))

    @classmethod
    def getCopyExpression(cls):
        return "value.copy()"

    @classmethod
    def correctValue(cls, value):
        if isinstance(value, Color): return value, 0
        else: return cls.getDefaultValue(), 2


class ColorListSocket(bpy.types.NodeSocket, CListSocket):
    bl_idname = "an_ColorListSocket"
    bl_label = "Color List Socket"
    dataType = "Color List"
    baseType = ColorSocket
    drawColor = (0.8, 0.8, 0.2, 0.5)
    storable = True
    comparable = False
    listClass = ColorList
