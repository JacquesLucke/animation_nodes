import bpy
from .. base_types.socket import AnimationNodeSocket

class ParticleSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_ParticleSocket"
    bl_label = "Particle Socket"
    dataType = "Particle"
    allowedInputTypes = ["Particle"]
    drawColor = (0.5, 0.3, 0.1, 1)
    storable = False
    comparable = True

    @classmethod
    def getDefaultValue(cls):
        return None

    @classmethod
    def getDefaultValueCode(self):
        return "None"


class ParticleListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_ParticleListSocket"
    bl_label = "Particle List Socket"
    dataType = "Particle List"
    baseDataType = "Particle"
    allowedInputTypes = ["Particle List"]
    drawColor = (0.5, 0.3, 0.1, 0.5)
    storable = False
    comparable = False

    @classmethod
    def getDefaultValueCode(self):
        return "[]"

    @classmethod
    def getCopyExpression(cls):
        return "value[:]"
