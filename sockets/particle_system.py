import bpy
from .. base_types.socket import AnimationNodeSocket

class ParticleSystemSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_ParticleSystemSocket"
    bl_label = "Particle System Socket"
    dataType = "Particle System"
    allowedInputTypes = ["Particle System"]
    drawColor = (1.0, 0.8, 0.6, 1)

    def getValueCode(self):
        return "None"
