import bpy
from .. mn_execution import nodePropertyChanged
from .. mn_node_base import *

class mn_ParticleSystemListSocket(mn_BaseSocket, mn_SocketProperties):
    bl_idname = "mn_ParticleSystemListSocket"
    bl_label = "Particle System List Socket"
    dataType = "Particle System List"
    allowedInputTypes = ["Particle System List"]
    drawColor = (1.0, 0.55, 0.55, 1)
    
    def drawInput(self, layout, node, text):
        layout.label(text)
        
    def getValue(self):
        return []
        
    def setStoreableValue(self, data):
        pass
    def getStoreableValue(self):
        pass
        
    def getCopyValueFunctionString(self):
        return "return value[:]"
