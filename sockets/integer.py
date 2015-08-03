import bpy
from .. events import propertyChanged
from .. base_types.socket import AnimationNodeSocket

def getValue(self):
    return min(max(self.min, self.get("value", 0)), self.max)
def setValue(self, value):
    self["value"] = min(max(self.min, value), self.max)

class IntegerSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "mn_IntegerSocket"
    bl_label = "Integer Socket"
    dataType = "Integer"
    allowedInputTypes = ["Integer"]
    drawColor = (0.2, 0.2, 1.0, 1.0)

    value = bpy.props.IntProperty(default = 0,
        set = setValue, get = getValue,
        update = propertyChanged)

    showName = bpy.props.BoolProperty(default = True)

    min = bpy.props.IntProperty(default = -10000000)
    max = bpy.props.IntProperty(default = 10000000)

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
