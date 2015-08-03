import bpy
from .. mn_execution import nodePropertyChanged
from .. mn_node_base import *

class mn_IntegerListSocket(mn_BaseSocket, mn_SocketProperties):
    bl_idname = "mn_IntegerListSocket"
    bl_label = "Integer List Socket"
    dataType = "Integer List"
    allowedInputTypes = ["Integer List"]
    drawColor = (0.2, 0.0, 0.9, 1.0)
    
    def drawInput(self, layout, node, text):
        layout.label(text)
        
    def getValue(self):
        return []
        
    def setStoreableValue(self, data):
        pass
    def getStoreableValue(self):
        return []
        
    def getCopyValueFunctionString(self):
        return "return value[:]"
