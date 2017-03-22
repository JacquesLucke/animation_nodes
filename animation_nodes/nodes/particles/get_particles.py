import bpy
from ... base_types import AnimationNode

class GetParticlesNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GetParticlesNode"
    bl_label = "Get Particles"

    def create(self):
        self.newInput("Particle System", "Particle System", "particleSystem")
        self.newOutput("Particle List", "Particles", "particles")

    def execute(self, particleSystem):
        if not particleSystem: return []
        return list(particleSystem.particles)
