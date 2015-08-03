import bpy
from .. mn_execution import nodePropertyChanged
from .. base_types.socket import AnimationNodeSocket
from .. data_structures.mesh import Polygon

class mn_PolygonSocket(bpy.types.NodeSocket, AnimationNodeSocket):
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