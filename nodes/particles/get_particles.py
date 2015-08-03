import bpy
from ... base_types.node import AnimationNode

class GetParticlesNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GetParticles"
    bl_label = "Get Particles"

    inputNames = { "Particle System" : "particleSystem" }
    outputNames = { "Particles" : "particles" }

    def create(self):
        self.inputs.new("an_ParticleSystemSocket", "Particle System")
        self.outputs.new("an_ParticleListSocket", "Particles")

    def execute(self, particleSystem):
        if not particleSystem: return []
        return list(particleSystem.particles)
