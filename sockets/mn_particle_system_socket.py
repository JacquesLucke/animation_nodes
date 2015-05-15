import bpy
from .. mn_execution import nodePropertyChanged
from .. mn_node_base import *

class mn_ParticleSystemSocket(mn_BaseSocket, mn_SocketProperties):
    bl_idname = "mn_ParticleSystemSocket"
    bl_label = "Particle System Socket"
    dataType = "Particle System"
    allowedInputTypes = ["Particle System"]
    drawColor = (1.0, 0.8, 0.6, 1)
    
    def drawInput(self, layout, node, text):
        layout.label(text)
        
    def getValue(self):
        return None
        
    def setStoreableValue(self, data):
        pass
    def getStoreableValue(self):
        pass
