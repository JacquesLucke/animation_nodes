import bpy
from .. mn_execution import nodePropertyChanged
from .. mn_node_base import *
from .. data_structures.curve import BezierCurve

class mn_BezierCurveSocket(mn_BaseSocket, mn_SocketProperties):
    bl_idname = "mn_BezierCurveSocket"
    bl_label = "Bezier Curve Socket"
    dataType = "Bezier Curve"
    allowedInputTypes = ["Bezier Curve"]
    drawColor = (0.3, 0.7, 0.18, 1)
    
    def drawInput(self, layout, node, text):
        layout.label(text)
        
    def getValue(self):
        return BezierCurve()
        
    def setStoreableValue(self, data):
        pass
    def getStoreableValue(self):
        pass

    def getCopyValueFunctionString(self):
        return "return value.copy()"