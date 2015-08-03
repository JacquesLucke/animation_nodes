import bpy
from ... base_types.node import AnimationNode

class GetParticlesNode(bpy.types.Node, AnimationNode):
    bl_idname = "mn_GetParticles"
    bl_label = "Get Particles"

    inputNames = { "Particle System" : "particleSystem" }
    outputNames = { "Particles" : "particles" }

    def create(self):
        self.inputs.new("mn_ParticleSystemSocket", "Particle System")
        self.outputs.new("mn_ParticleListSocket", "Particles")

    def execute(self, particleSystem):
        if not particleSystem: return []
        return list(particleSystem.particles)
