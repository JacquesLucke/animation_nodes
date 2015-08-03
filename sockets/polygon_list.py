import bpy
from .. mn_execution import nodePropertyChanged
from .. base_types.socket import AnimationNodeSocket
from mathutils import Matrix

class mn_PolygonListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "mn_PolygonListSocket"
    bl_label = "Polygon List Socket"
    dataType = "Polygon List"
    allowedInputTypes = ["Polygon List"]
    drawColor = (0.25, 0.55, 0.23, 1)
    recreateValueOnEachUse = True
    
    def drawInput(self, layout, node, text):
        layout.label(text)
        
    def getValue(self):
        return []
        
    def setStoreableValue(self, data):
        pass
    def getStoreableValue(self):
        pass
