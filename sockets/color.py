import bpy
from .. events import propertyChanged
from .. base_types.socket import AnimationNodeSocket

class ColorSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "mn_ColorSocket"
    bl_label = "Color Socket"
    dataType = "Color"
    allowedInputTypes = ["Color"]
    drawColor = (0.8, 0.8, 0.2, 1)

    value = bpy.props.FloatVectorProperty(
        default = [0.5, 0.5, 0.5], subtype = "COLOR",
        soft_min = 0.0, soft_max = 1.0,
        update = propertyChanged)

    def drawInput(self, layout, node, text):
        layout.prop(self, "value", text = text)

    def getValue(self):
        return list(self.value) + [1.0]

    def setStoreableValue(self, data):
        self.value = data[:3]

    def getStoreableValue(self):
        return self.value

    def getCopyValueFunctionString(self):
        return "return value[:]"
