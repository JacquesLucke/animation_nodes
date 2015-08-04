import bpy
from bpy.props import *
from .. events import propertyChanged
from .. base_types.socket import AnimationNodeSocket

def getValue(self):
    return min(max(self.min, self.get("value", 0)), self.max)
def setValue(self, value):
    self["value"] = min(max(self.min, value), self.max)

class FloatSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_FloatSocket"
    bl_label = "Float Socket"
    dataType = "Float"
    allowedInputTypes = ["Float", "Integer"]
    drawColor = (0.4, 0.4, 0.7, 1)

    value = FloatProperty(default = 0.0,
        set = setValue, get = getValue,
        update = propertyChanged)

    showName = bpy.props.BoolProperty(default = True)

    min = bpy.props.FloatProperty(default = -10000000)
    max = bpy.props.FloatProperty(default = 10000000)

    def drawInput(self, layout, node, text):
        if not self.showName: text = ""
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
        return str(round(self.value, 3))
