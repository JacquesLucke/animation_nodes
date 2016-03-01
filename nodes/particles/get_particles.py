import bpy
from ... base_types.node import AnimationNode

class GetParticlesNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GetParticlesNode"
    bl_label = "Get Particles"

    def create(self):
        self.inputs.new("an_ParticleSystemSocket", "Particle System", "particleSystem")
        self.outputs.new("an_ParticleListSocket", "Particles", "particles")

    def execute(self, particleSystem):
        if not particleSystem: return []
        return list(particleSystem.particles)
