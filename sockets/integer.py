import bpy
from bpy.props import *
from .. events import propertyChanged
from .. base_types.socket import AnimationNodeSocket

def getValue(self):
    return min(max(self.minValue, self.get("value", 0)), self.maxValue)
def setValue(self, value):
    self["value"] = min(max(self.minValue, value), self.maxValue)

class IntegerSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_IntegerSocket"
    bl_label = "Integer Socket"
    dataType = "Integer"
    allowedInputTypes = ["Integer"]
    drawColor = (0.3, 0.4, 1.0, 1.0)
    hashable = True
    storable = True

    value = IntProperty(default = 0,
        set = setValue, get = getValue,
        update = propertyChanged)

    minValue = IntProperty(default = -2**31)
    maxValue = IntProperty(default = 2**31-1)

    def drawProperty(self, layout, text):
        layout.prop(self, "value", text = text)

    def getValue(self):
        return self.value

    def setProperty(self, data):
        self.value = data

    def getProperty(self):
        return self.value

    def setRange(self, min, max):
        self.minValue = min
        self.maxValue = max
