import bpy
from .. mn_execution import nodePropertyChanged
from .. base_types.socket import AnimationNodeSocket

class mn_ParticleSystemSocket(bpy.types.NodeSocket, AnimationNodeSocket):
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
