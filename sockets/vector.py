import bpy
from bpy.props import *
from mathutils import Vector
from .. events import propertyChanged
from .. base_types.socket import AnimationNodeSocket

class VectorSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_VectorSocket"
    bl_label = "Vector Socket"
    dataType = "Vector"
    allowedInputTypes = ["Vector"]
    drawColor = (0.05, 0.05, 0.8, 0.7)

    value = FloatVectorProperty(default = [0, 0, 0], update = propertyChanged)

    def drawProperty(self, layout, text):
        col = layout.column(align = True)
        if text != "": col.label(text)
        col.prop(self, "value", index = 0, text = "X")
        col.prop(self, "value", index = 1, text = "Y")
        col.prop(self, "value", index = 2, text = "Z")

    def getValue(self):
        return Vector(self.value)

    def setProperty(self, data):
        self.value = data

    def getProperty(self):
        return self.value[:]

    def getCopyStatement(self):
        return "value.copy()"
