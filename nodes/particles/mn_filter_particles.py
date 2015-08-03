import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types.node import AnimationNode


class FilterParticles(bpy.types.Node, AnimationNode):
    bl_idname = "mn_FilterParticles"
    bl_label = "Filter Particles"

    inputNames = { "Particles" : "particles" }
    outputNames = { "Particles" : "filteredParticles" }

    outputUnborn = BoolProperty(name = "Output Unborn Particles", default = False, update = propertyChanged)
    outputAlive = BoolProperty(name = "Output Alive Particles", default = True, update = propertyChanged)
    outputDying = BoolProperty(name = "Output Dying Particles", default = False, update = propertyChanged)
    outputDead = BoolProperty(name = "Output Dead Particles", default = False, update = propertyChanged)

    def create(self):
        self.inputs.new("mn_ParticleListSocket", "Particles")
        self.outputs.new("mn_ParticleListSocket", "Particles")

    def draw_buttons(self, context, layout):
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
