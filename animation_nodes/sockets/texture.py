import bpy
from bpy.props import *
from bpy.types import Texture
from .. events import propertyChanged
from .. base_types import AnimationNodeSocket, PythonListSocket

class TextureSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_TextureSocket"
    bl_label = "Texture Socket"
    dataType = "Texture"
    drawColor = (0.65, 0.1, 1.0, 1)
    storable = False
    comparable = True

    texture: PointerProperty(type = Texture, update = propertyChanged)

    def drawProperty(self, layout, text, node):
        row = layout.row(align = True)
        row.prop(self, "texture", text = text)

    def getValue(self):
        return self.texture

    def setProperty(self, data):
        self.texture = data

    def getProperty(self):
        return self.texture

    @classmethod
    def getDefaultValue(cls):
        return None

    @classmethod
    def correctValue(cls, value):
        if isinstance(value, Texture) or value is None:
            return value, 0
        return cls.getDefaultValue(), 2


class TextureListSocket(bpy.types.NodeSocket, PythonListSocket):
    bl_idname = "an_TextureListSocket"
    bl_label = "Texture List Socket"
    dataType = "Texture List"
    baseType = TextureSocket
    drawColor = (0.65, 0.1, 1.0, 0.5)
    storable = False
    comparable = False

    @classmethod
    def getCopyExpression(cls):
        return "value[:]"

    @classmethod
    def correctValue(cls, value):
        if isinstance(value, list):
            if all(isinstance(element, Texture) or element is None for element in value):
                return value, 0
        return cls.getDefaultValue(), 2