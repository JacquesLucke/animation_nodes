import bpy
from .. base_types.socket import AnimationNodeSocket

class ParticleListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_ParticleListSocket"
    bl_label = "Particle List Socket"
    dataType = "Particle List"
    allowedInputTypes = ["Particle List"]
    drawColor = (0.5, 0.3, 0.1, 0.5)
    storable = False
    hashable = False

    def getValueCode(self):
        return "[]"

    def getCopyExpression(self):
        return "value[:]"
