import bpy
from .. mn_execution import nodePropertyChanged
from .. base_types.socket import AnimationNodeSocket

class mn_ColorSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "mn_ColorSocket"
    bl_label = "Color Socket"
    dataType = "Color"
    allowedInputTypes = ["Color"]
    drawColor = (0.8, 0.8, 0.2, 1)
    
    value = bpy.props.FloatVectorProperty(default = [0.5, 0.5, 0.5], subtype = "COLOR", soft_min = 0.0, soft_max = 1.0, update = nodePropertyChanged)
    
    def drawInput(self, layout, node, text):
        layout.prop(self, "value", text = text)
        
    def getValue(self):
        value = self.value
        return [value[0], value[1], value[2], 1.0]
        
    def setStoreableValue(self, data):
        self.value = data[:3]
    def getStoreableValue(self):
        return self.value
        
    def getCopyValueFunctionString(self):
        return "return value[:]"
