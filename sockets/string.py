import bpy
from bpy.props import *
from .. events import propertyChanged
from .. base_types.socket import AnimationNodeSocket, ListSocket


class StringSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_StringSocket"
    bl_label = "String Socket"
    dataType = "String"
    allowedInputTypes = ["String"]
    drawColor = (1, 1, 1, 1)
    comparable = True
    storable = True

    value = StringProperty(default = "", update = propertyChanged, options = {"TEXTEDIT_UPDATE"})

    showFileChooser = BoolProperty(default = False)

    def drawProperty(self, layout, text, node):
        row = layout.row(align = True)
        row.prop(self, "value", text = text)
        if self.showFileChooser:
            self.invokePathChooser(row, node, "setPath", icon = "EYEDROPPER")

    def getValue(self):
        return self.value

    def setProperty(self, data):
        self.value = data

    def getProperty(self):
        return self.value

    def setPath(self, path):
        self.value = path

    @classmethod
    def getDefaultValue(cls):
        return ""

    @classmethod
    def correctValue(cls, value):
        if isinstance(value, str):
            return value, 0
        return str(value), 1


class StringListSocket(bpy.types.NodeSocket, ListSocket, AnimationNodeSocket):
    bl_idname = "an_StringListSocket"
    bl_label = "String List Socket"
    dataType = "String List"
    baseDataType = "String"
    allowedInputTypes = ["String List"]
    drawColor = (1, 1, 1, 0.5)
    storable = True
    comparable = False

    @classmethod
    def getCopyExpression(cls):
        return "value[:]"

    @classmethod
    def correctValue(cls, value):
        if isinstance(value, list):
            if all(isinstance(element, str) for element in value):
                return value, 0
            else:
                return list(map(str, value)), 1
        return cls.getDefaultValue(), 2
