import bpy
from bpy.props import *
from .. mn_execution import nodePropertyChanged
from .. base_types.socket import AnimationNodeSocket

def getValue(self):
    return min(max(self.min, self.get("value", 0)), self.max)
def setValue(self, value):
    self["value"] = min(max(self.min, value), self.max)

class FloatSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "mn_FloatSocket"
    bl_label = "Float Socket"
    dataType = "Float"
    allowedInputTypes = ["Float", "Integer"]
    drawColor = (0.4, 0.4, 0.7, 1)

    value = FloatProperty(default = 0.0, 
        set = setValue, get = getValue,
        update = nodePropertyChanged)

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
