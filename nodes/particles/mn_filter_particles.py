import bpy, random, mathutils
from bpy.types import Node
from bpy.props import *
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling


class mn_FilterParticles(Node, AnimationNode):
    bl_idname = "mn_FilterParticles"
    bl_label = "Filter Particles"
    
    outputUnborn = BoolProperty(name = "Output Unborn Particles", default = False)
    outputAlive = BoolProperty(name = "Output Alive Particles", default = True)
    outputDying = BoolProperty(name = "Output Dying Particles", default = False)
    outputDead = BoolProperty(name = "Output Dead Particles", default = False)
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_ParticleListSocket", "Particles")
        self.outputs.new("mn_ParticleListSocket", "Particles")
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        col = layout.column()
        col.prop(self, "outputUnborn", text = "Unborn")
        col.prop(self, "outputAlive", text = "Alive")
        col.prop(self, "outputDying", text = "Dying")
        col.prop(self, "outputDead", text = "Dead")
        
    def getInputSocketNames(self):
        return {"Particles" : "particles"}
    def getOutputSocketNames(self):
        return {"Particles" : "filteredParticles"}

    def execute(self, particles):
        filteredParticles = []
        for particle in particles:
            if particle.alive_state == "UNBORN" and self.outputUnborn or \
                particle.alive_state == "ALIVE" and self.outputAlive or \
                particle.alive_state == "DYING" and self.outputDead or \
                particle.alive_state == "DEAD" and self.outputDead:
                filteredParticles.append(particle)
        return filteredParticles
        