import bpy
from animation_nodes.mn_execution import nodePropertyChanged
from animation_nodes.mn_node_base import *

class mn_ColorSocket(mn_BaseSocket, mn_SocketProperties):
    bl_idname = "mn_ColorSocket"
    bl_label = "Color Socket"
    dataType = "Color"
    allowedInputTypes = ["Color"]
    drawColor = (0.8, 0.8, 0.2, 1)
    
    color = bpy.props.FloatVectorProperty(default = [0.5, 0.5, 0.5], subtype = "COLOR", soft_min = 0.0, soft_max = 1.0, update = nodePropertyChanged)
    
    def drawInput(self, layout, node, text):
        layout.prop(self, "color", text = text)
        
    def getValue(self):
        color = self.color
        return [color[0], color[1], color[2], 1.0]
        
    def setStoreableValue(self, data):
        self.color = data[:3]
    def getStoreableValue(self):
        return self.color
        
    def getCopyValueFunctionString(self):
        return "return value[:]"
