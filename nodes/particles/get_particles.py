import bpy
from ... base_types.node import AnimationNode

class GetParticlesNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GetParticlesNode"
    bl_label = "Get Particles"

    def create(self):
        self.newInput("an_ParticleSystemSocket", "Particle System", "particleSystem")
        self.newOutput("an_ParticleListSocket", "Particles", "particles")

    def execute(self, particleSystem):
        if not particleSystem: return []
        return list(particleSystem.particles)
