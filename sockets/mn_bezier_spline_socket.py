import bpy
from .. mn_execution import nodePropertyChanged
from .. mn_node_base import *
from .. data_structures.curve import BezierSpline

class mn_BezierSplineSocket(mn_BaseSocket, mn_SocketProperties):
    bl_idname = "mn_BezierSplineSocket"
    bl_label = "Bezier Spline Socket"
    dataType = "Bezier Spline"
    allowedInputTypes = ["Bezier Spline"]
    drawColor = (0.5, 0.7, 0.18, 1)
    
    def drawInput(self, layout, node, text):
        layout.label(text)
        
    def getValue(self):
        return BezierSpline()
        
    def setStoreableValue(self, data):
        pass
    def getStoreableValue(self):
        pass

    def getCopyValueFunctionString(self):
        return "return value.copy()"