import bpy
from bpy.props import *
from .. events import propertyChanged
from .. base_types.socket import AnimationNodeSocket

def getValue(self):
    return min(max(self.min, self.get("value", 0)), self.max)
def setValue(self, value):
    self["value"] = min(max(self.min, value), self.max)

class IntegerSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_IntegerSocket"
    bl_label = "Integer Socket"
    dataType = "Integer"
    allowedInputTypes = ["Integer"]
    drawColor = (0.2, 0.2, 1.0, 1.0)

    value = IntProperty(default = 0,
        set = setValue, get = getValue,
        update = propertyChanged)

    showName = BoolProperty(default = True)

    min = IntProperty(default = -2**31)
    max = IntProperty(default = 2**31-1)

    def drawInput(self, layout, node, text):
        if not self.showName: text = ""
        self.drawAsProperty(layout, text)

    def drawAsProperty(self, layout, text):
        layout.prop(self, "value", text = text)

    def getValue(self):
        return self.value

    def setStoreableValue(self, data):
        self.value = data

    def getStoreableValue(self):
        return self.value

    def setMinMax(self, min, max):
        self.min = min
        self.max = max

    def toString(self):
        if self.showName: return self.getDisplayedName()
        return str(self.value)
