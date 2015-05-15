import bpy
from .. mn_execution import nodePropertyChanged
from .. mn_node_base import *

class mn_BezierSplineListSocket(mn_BaseSocket, mn_SocketProperties):
    bl_idname = "mn_BezierSplineListSocket"
    bl_label = "Bezier Spline List Socket"
    dataType = "Bezier Spline List"
    allowedInputTypes = ["Bezier Spline List"]
    drawColor = (0.3, 0.7, 1, 0.6)
    
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
