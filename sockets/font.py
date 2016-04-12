import bpy
from bpy.props import *
from .. events import propertyChanged
from .. base_types.socket import AnimationNodeSocket

class FontSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_FontSocket"
    bl_label = "Font Socket"
    dataType = "Font"
    allowedInputTypes = ["Font"]
    drawColor = (0.444, 0.444, 0, 1)
    storable = False
    comparable = True

    fontName = StringProperty(update = propertyChanged)

    def drawProperty(self, layout, text):
        row = layout.row(align = True)
        row.prop_search(self, "fontName",  bpy.data, "fonts", icon = "NONE", text = text)
        self.invokeFunction(row, "assignFontOfActiveObject", icon = "EYEDROPPER")

    def getValue(self):
        return bpy.data.fonts.get(self.fontName)

    def setProperty(self, data):
        self.fontName = data

    def getProperty(self):
        return self.fontName

    def assignFontOfActiveObject(self):
        object = bpy.context.active_object
        if object.type == "FONT":
            self.fontName = object.data.font.name


class FontListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_FontListSocket"
    bl_label = "Font List Socket"
    dataType = "Font List"
    allowedInputTypes = ["Font List"]
    drawColor = (0.444, 0.444, 0, 0.5)
    storable = False
    comparable = False

    def getValueCode(self):
        return "[]"

    @classmethod
    def getCopyExpression(cls):
        return "value[:]"
