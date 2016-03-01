import bpy
from bpy.props import *
from .. events import propertyChanged
from .. base_types.socket import AnimationNodeSocket

class ColorSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_ColorSocket"
    bl_label = "Color Socket"
    dataType = "Color"
    allowedInputTypes = ["Color"]
    drawColor = (0.8, 0.8, 0.2, 1)
    storable = True
    hashable = False

    value = FloatVectorProperty(
        default = [0.5, 0.5, 0.5], subtype = "COLOR",
        soft_min = 0.0, soft_max = 1.0,
        update = propertyChanged)

    def drawProperty(self, layout, text):
        layout.prop(self, "value", text = text)

    def getValue(self):
        return list(self.value) + [1.0]

    def setProperty(self, data):
        self.value = data[:3]

    def getProperty(self):
        return self.value

    def getCopyExpression(self):
        return "value[:]"
