import bpy
from .. mn_execution import nodePropertyChanged
from .. mn_node_base import *
from .. utils.mn_mesh_utils import Vertex

class mn_VertexSocket(mn_BaseSocket, mn_SocketProperties):
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
