import bpy
from .. mn_execution import nodePropertyChanged
from .. base_types.socket import AnimationNodeSocket

class mn_ParticleSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "mn_ParticleSocket"
    bl_label = "Particle Socket"
    dataType = "Particle"
    allowedInputTypes = ["Particle"]
    drawColor = (0.5, 0.3, 0.1, 1)
    
    def drawInput(self, layout, node, text):
        layout.label(text)
        
    def getValue(self):
        return None
        
    def setStoreableValue(self, data):
        pass
    def getStoreableValue(self):
        pass
