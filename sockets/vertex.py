import bpy
from .. mn_execution import nodePropertyChanged
from .. base_types.socket import AnimationNodeSocket
from .. data_structures.mesh import Vertex

class mn_VertexSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "mn_VertexSocket"
    bl_label = "Vertex Socket"
    dataType = "Vertex"
    allowedInputTypes = ["Vertex"]
    drawColor = (0.6, 0.8, 0.36, 1)
    
    def drawInput(self, layout, node, text):
        layout.label(text)
        
    def getValue(self):
        return Vertex()
        
    def setStoreableValue(self, data):
        pass
    def getStoreableValue(self):
        pass
