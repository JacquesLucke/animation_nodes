import bpy
from bpy.props import *
from ... events import executionCodeChanged
from ... base_types import AnimationNode

class FilterParticlesNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_FilterParticlesNode"
    bl_label = "Filter Particles"

    outputUnborn = BoolProperty(name = "Output Unborn Particles", default = False, update = executionCodeChanged)
    outputAlive = BoolProperty(name = "Output Alive Particles", default = True, update = executionCodeChanged)
    outputDying = BoolProperty(name = "Output Dying Particles", default = False, update = executionCodeChanged)
    outputDead = BoolProperty(name = "Output Dead Particles", default = False, update = executionCodeChanged)

    def create(self):
        self.newInput("Particle List", "Particles", "particles")
        self.newOutput("Particle List", "Particles", "filteredParticles")

    def draw(self, layout):
        col = layout.column(align = True)
        col.prop(self, "outputUnborn", text = "Unborn")
        col.prop(self, "outputAlive", text = "Alive")
        col.prop(self, "outputDying", text = "Dying")
        col.prop(self, "outputDead", text = "Dead")

    def getExecutionCode(self):
        condition = " or ".join("particle.alive_state == '{}'".format(state) for state in self.iterAllowedAliveStates())

        if condition == "":
            yield "filteredParticles = []"
        else:
            yield "try: filteredParticles = [particle for particle in particles if {}]".format(condition)
            yield "except:"
            yield "    for particle in particles:"
            yield "        if particle is not None:"
            yield "            if {}: filteredParticles.append(particle)".format(condition)

    def iterAllowedAliveStates(self):
        if self.outputUnborn: yield "UNBORN"
        if self.outputAlive: yield "ALIVE"
        if self.outputDying: yield "DYING"
        if self.outputDead: yield "DEAD"
