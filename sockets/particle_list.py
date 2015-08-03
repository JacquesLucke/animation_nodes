import bpy
from .. mn_execution import nodePropertyChanged
from .. base_types.socket import AnimationNodeSocket

class mn_ParticleListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "mn_ParticleListSocket"
    bl_label = "Particle List Socket"
    dataType = "Particle List"
    allowedInputTypes = ["Particle List"]
    drawColor = (0.7, 0.5, 0.3, 1)
    
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
