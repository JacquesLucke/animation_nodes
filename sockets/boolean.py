import bpy
from .. mn_execution import nodePropertyChanged
from .. base_types.socket import AnimationNodeSocket

class mn_BooleanSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "mn_BooleanSocket"
    bl_label = "Boolean Socket"
    dataType = "Boolean"
    allowedInputTypes = ["Boolean"]
    drawColor = (0.7, 0.7, 0.4, 1)

    value = bpy.props.BoolProperty(default = True, update = nodePropertyChanged)

    def drawInput(self, layout, node, text):
        layout.prop(self, "value", text = text)

    def getValue(self):
        return self.value

    def setStoreableValue(self, data):
        self.value = data

    def getStoreableValue(self):
        return self.value
