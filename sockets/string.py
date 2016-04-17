import bpy
from bpy.props import *
from .. events import propertyChanged
from .. base_types.socket import AnimationNodeSocket


class StringSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_StringSocket"
    bl_label = "String Socket"
    dataType = "String"
    allowedInputTypes = ["String"]
    drawColor = (1, 1, 1, 1)
    comparable = True
    storable = True

    value = StringProperty(default = "", update = propertyChanged, options = {"TEXTEDIT_UPDATE"})

    def drawProperty(self, layout, text):
        layout.prop(self, "value", text = text)

    def getValue(self):
        return self.value

    def setProperty(self, data):
        self.value = data

    def getProperty(self):
        return self.value

    @classmethod
    def getDefaultValue(cls):
        return ""


class StringListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_StringListSocket"
    bl_label = "String List Socket"
    dataType = "String List"
    baseDataType = "String"
    allowedInputTypes = ["String List"]
    drawColor = (1, 1, 1, 0.5)
    storable = True
    comparable = False

    @classmethod
    def getDefaultValue(cls):
        return []

    @classmethod
    def getDefaultValueCode(self):
        return "[]"

    @classmethod
    def getCopyExpression(cls):
        return "value[:]"
