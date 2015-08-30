import bpy
from .. base_types.socket import AnimationNodeSocket

class ParticleListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_ParticleListSocket"
    bl_label = "Particle List Socket"
    dataType = "Particle List"
    allowedInputTypes = ["Particle List"]
    drawColor = (0.7, 0.5, 0.3, 1)

    def getValue(self):
        return []

    def getValueCode(self):
        return "[]"

    def getCopyStatement(self):
        return "value[:]"
