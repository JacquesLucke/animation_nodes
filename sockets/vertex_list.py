import bpy
from .. mn_execution import nodePropertyChanged
from .. base_types.socket import AnimationNodeSocket
from mathutils import Matrix

class mn_VertexListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "mn_VertexListSocket"
    bl_label = "Vertex List Socket"
    dataType = "Vertex List"
    allowedInputTypes = ["Vertex List"]
    drawColor = (0.3, 1.0, 0.4, 1.0)
    
    def drawInput(self, layout, node, text):
        layout.label(text)
        
    def getValue(self):
        return []
        
    def setStoreableValue(self, data):
        pass
    def getStoreableValue(self):
        pass
