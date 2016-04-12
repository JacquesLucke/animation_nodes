import bpy
from .. base_types.socket import AnimationNodeSocket

class ParticleSystemSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_ParticleSystemSocket"
    bl_label = "Particle System Socket"
    dataType = "Particle System"
    allowedInputTypes = ["Particle System"]
    drawColor = (1.0, 0.8, 0.6, 1)
    storable = False
    comparable = True

    def getValueCode(self):
        return "None"


class ParticleSystemListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_ParticleSystemListSocket"
    bl_label = "Particle System List Socket"
    dataType = "Particle System List"
    allowedInputTypes = ["Particle System List"]
    drawColor = (1.0, 0.8, 0.6, 0.5)
    storable = False
    comparable = False

    def getValueCode(self):
        return "[]"

    @classmethod
    def getCopyExpression(cls):
        return "value[:]"
