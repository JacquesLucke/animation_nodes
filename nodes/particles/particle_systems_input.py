import bpy
from ... base_types.node import AnimationNode

class ParticleSystemsInputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ParticleSystemsInputNode"
    bl_label = "Particle Systems Input"
    bl_width_default = 150

    def create(self):
        self.newInput("Object", "Object", "object", defaultDrawType = "PROPERTY_ONLY")
        self.newOutput("Particle System List", "Particle Systems", "particleSystems")
        self.newOutput("Particle System", "Active", "active")

    def execute(self, object):
        if not object: return [], None
        particleSystems = object.particle_systems
        active = particleSystems.active
        return list(particleSystems), active
