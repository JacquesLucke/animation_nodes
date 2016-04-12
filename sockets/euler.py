import bpy
from bpy.props import *
from mathutils import Euler
from .. events import propertyChanged
from .. base_types.socket import AnimationNodeSocket

class EulerSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_EulerSocket"
    bl_label = "Euler Socket"
    dataType = "Euler"
    allowedInputTypes = ["Euler"]
    drawColor = (0.1, 0.0, 0.4, 1.0)
    storable = True
    comparable = False

    value = FloatVectorProperty(default = [0, 0, 0], update = propertyChanged, subtype = "EULER")

    def drawProperty(self, layout, text):
        col = layout.column(align = True)
        if text != "": col.label(text)
        col.prop(self, "value", index = 0, text = "X")
        col.prop(self, "value", index = 1, text = "Y")
        col.prop(self, "value", index = 2, text = "Z")

    def getValue(self):
        return Euler(self.value)

    def setProperty(self, data):
        self.value = data

    def getProperty(self):
        return self.value[:]

    @classmethod
    def getCopyExpression(cls):
        return "value.copy()"


class EulerListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_EulerListSocket"
    bl_label = "Euler List Socket"
    dataType = "Euler List"
    baseDataType = "Euler"
    allowedInputTypes = ["Euler List"]
    drawColor = (0.1, 0.0, 0.4, 0.5)
    storable = True
    comparable = False

    def getValueCode(self):
        return "[]"

    @classmethod
    def getCopyExpression(cls):
        return "[element.copy() for element in value]"
