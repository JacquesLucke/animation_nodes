import bpy
from .. mn_execution import nodePropertyChanged
from .. mn_node_base import *

class mn_BezierPointListSocket(mn_BaseSocket, mn_SocketProperties):
    bl_idname = "mn_BezierPointListSocket"
    bl_label = "Bezier Point List Socket"
    dataType = "Bezier Point List"
    allowedInputTypes = ["Bezier Point List"]
    drawColor = (0.5, 0.5, 1, 0.6)
    
    def drawInput(self, layout, node, text):
        layout.label(text)
        
    def getValue(self):
        return []
        
    def setStoreableValue(self, data):
        pass
    def getStoreableValue(self):
        return []
        
    def getCopyValueFunctionString(self):
        return "return [element.copy() for element in value]"
