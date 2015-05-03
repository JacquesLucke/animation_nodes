import bpy
from animation_nodes.mn_execution import nodePropertyChanged
from animation_nodes.mn_node_base import *

class mn_EdgeIndicesSocket(mn_BaseSocket, mn_SocketProperties):
    bl_idname = "mn_EdgeIndicesSocket"
    bl_label = "Edge Indices Socket"
    dataType = "Edge Indices"
    allowedInputTypes = ["Edge Indices"]
    drawColor = (1.0, 0.55, 0.23, 1)
    
    def drawInput(self, layout, node, text):
        layout.label(text)
        
    def getValue(self):
        return (0, 1)
        
    def setStoreableValue(self, data):
        pass
    def getStoreableValue(self):
        pass
        
    def getCopyValueFunctionString(self):
        return "return value[:]"
