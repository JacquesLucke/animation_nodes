import bpy
from .. mn_execution import nodePropertyChanged
from .. mn_node_base import *
from .. data_structures.mesh import Polygon

class mn_PolygonSocket(mn_BaseSocket, mn_SocketProperties):
    bl_idname = "mn_PolygonSocket"
    bl_label = "Polygon Socket"
    dataType = "Polygon"
    allowedInputTypes = ["Polygon"]
    drawColor = (0.14, 0.34, 0.19, 1)
    
    def drawInput(self, layout, node, text):
        layout.label(text)
        
    def getValue(self):
        return Polygon()
        
    def setStoreableValue(self, data):
        pass
    def getStoreableValue(self):
        pass