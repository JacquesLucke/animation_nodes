import bpy, random, mathutils
from ... base_types.node import AnimationNode

class ParticleSystemsInput(bpy.types.Node, AnimationNode):
    bl_idname = "mn_ParticleSystemsInput"
    bl_label = "Particle Systems Input"

    inputNames = { "Object" : "object" }

    outputNames = { "Particle Systems" : "particleSystems",
                    "Active" : "active"}

    def create(self):
        self.inputs.new("mn_ObjectSocket", "Object").showName = False
        self.outputs.new("mn_ParticleSystemListSocket", "Particle Systems")
        self.outputs.new("mn_ParticleSystemSocket", "Active")
        self.width += 10

    def execute(self, object):
        if not object: return [], None
        particleSystems = object.particle_systems
        active = particleSystems.active
        return list(particleSystems), active
