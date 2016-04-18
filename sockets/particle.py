import bpy
from bpy.types import Particle
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

    @classmethod
    def correctValue(cls, value):
        if isinstance(value, Particle) or value is None:
            return value, 0
        return cls.getDefaultValue(), 2


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
    def getDefaultValue(cls):
        return []

    @classmethod
    def getDefaultValueCode(self):
        return "[]"

    @classmethod
    def getCopyExpression(cls):
        return "value[:]"

    @classmethod
    def correctValue(cls, value):
        if isinstance(value, list):
            if all(isinstance(element, Particle) or element is None for element in value):
                return value, 0
        return cls.getDefaultValue(), 2
