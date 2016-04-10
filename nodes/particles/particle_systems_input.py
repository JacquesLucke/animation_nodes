import bpy, random, mathutils
from ... base_types.node import AnimationNode

class ParticleSystemsInputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ParticleSystemsInputNode"
    bl_label = "Particle Systems Input"

    def create(self):
        self.newInput("an_ObjectSocket", "Object", "object").defaultDrawType = "PROPERTY_ONLY"
        self.newOutput("an_ParticleSystemListSocket", "Particle Systems", "particleSystems")
        self.newOutput("an_ParticleSystemSocket", "Active", "active")
        self.width += 10

    def execute(self, object):
        if not object: return [], None
        particleSystems = object.particle_systems
        active = particleSystems.active
        return list(particleSystems), active
