import bpy
from bpy.props import *
from bpy.types import VectorFont
from .. events import propertyChanged
from .. base_types import AnimationNodeSocket, PythonListSocket

class FontSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_FontSocket"
    bl_label = "Font Socket"
    dataType = "Font"
    drawColor = (0.444, 0.444, 0, 1)
    storable = False
    comparable = True

    font: PointerProperty(type = VectorFont, update = propertyChanged)

    def drawProperty(self, layout, text, node):
        row = layout.row(align = True)
        row.prop(self, "font", text = text)
        self.invokeFunction(row, node, "assignFontOfActiveObject", icon = "EYEDROPPER")

    def getValue(self):
        return self.font

    def setProperty(self, data):
        self.font = data

    def getProperty(self):
        return self.font

    def assignFontOfActiveObject(self):
        object = bpy.context.active_object
        if getattr(object, "type", "") == "FONT":
            self.font = object.data.font

    @classmethod
    def getDefaultValue(cls):
        return None

    @classmethod
    def correctValue(cls, value):
        if isinstance(value, VectorFont) or value is None:
            return value, 0
        return cls.getDefaultValue(), 2


class FontListSocket(bpy.types.NodeSocket, PythonListSocket):
    bl_idname = "an_FontListSocket"
    bl_label = "Font List Socket"
    dataType = "Font List"
    baseType = FontSocket
    drawColor = (0.444, 0.444, 0, 0.5)
    storable = False
    comparable = False

    @classmethod
    def getCopyExpression(cls):
        return "value[:]"

    @classmethod
    def correctValue(cls, value):
        if isinstance(value, list):
            if all(isinstance(element, VectorFont) or element is None for element in value):
                return value, 0
        return cls.getDefaultValue(), 2
