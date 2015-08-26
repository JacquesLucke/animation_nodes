import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types.node import AnimationNode

class FilterParticlesNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_FilterParticlesNode"
    bl_label = "Filter Particles"

    outputUnborn = BoolProperty(name = "Output Unborn Particles", default = False, update = propertyChanged)
    outputAlive = BoolProperty(name = "Output Alive Particles", default = True, update = propertyChanged)
    outputDying = BoolProperty(name = "Output Dying Particles", default = False, update = propertyChanged)
    outputDead = BoolProperty(name = "Output Dead Particles", default = False, update = propertyChanged)

    def create(self):
        self.inputs.new("an_ParticleListSocket", "Particles", "particles")
        self.outputs.new("an_ParticleListSocket", "Particles", "filteredParticles")

    def draw(self, layout):
        col = layout.column()
        col.prop(self, "outputUnborn", text = "Unborn")
        col.prop(self, "outputAlive", text = "Alive")
        col.prop(self, "outputDying", text = "Dying")
        col.prop(self, "outputDead", text = "Dead")

    def execute(self, particles):
        filteredParticles = []
        for particle in particles:
            if particle.alive_state == "UNBORN" and self.outputUnborn or \
                particle.alive_state == "ALIVE" and self.outputAlive or \
                particle.alive_state == "DYING" and self.outputDead or \
                particle.alive_state == "DEAD" and self.outputDead:
                filteredParticles.append(particle)
        return filteredParticles
