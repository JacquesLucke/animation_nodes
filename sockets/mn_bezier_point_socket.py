import bpy
from .. mn_execution import nodePropertyChanged
from .. mn_node_base import *
from .. data_structures.curve import BezierPoint

class mn_BezierPointSocket(mn_BaseSocket, mn_SocketProperties):
    bl_idname = "mn_BezierPointSocket"
    bl_label = "Bezier Point Socket"
    dataType = "Bezier Point"
    allowedInputTypes = ["Bezier Point"]
    drawColor = (0.98, 0.7, 1.0, 1)
    
    def drawInput(self, layout, node, text):
        layout.label(text)
        
    def getValue(self):
        return BezierPoint()
        
    def setStoreableValue(self, data):
        pass
    def getStoreableValue(self):
        pass

    def getCopyValueFunctionString(self):
        return "return value.copy()"