from itertools import chain
import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode, VectorizedSocket
from ... events import executionCodeChanged

class ParticlesOutputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ParticlesOutputNode"
    bl_label = "Particles Output"
    bl_width_default = 180

    def checkedPropertiesChanged(self, context):
        self.updateSocketVisibility()
        propertyChanged()
        executionCodeChanged()

    locBool: BoolProperty(update = checkedPropertiesChanged)
    velBool: BoolProperty(update = checkedPropertiesChanged)
    rotBool: BoolProperty(update = checkedPropertiesChanged)
    dieBool: BoolProperty(update = checkedPropertiesChanged)

    def draw(self, layout):
        col = layout.column(align = True)
        row = col.row(align = True)
        row.prop(self, "locBool", text = "Locations", toggle = True)
        row.prop(self, "velBool", text = "Velocities", toggle = True)
        row = col.row(align = True)
        row.prop(self, "rotBool", text = "Rotations", toggle = True)
        row.prop(self, "dieBool", text = "Die Times", toggle = True)

    def create(self):
        self.newInput("Particle System", "Particle System", "particleSystem")
        self.newInput("Vector List", "Locations", "locations")
        self.newInput("Vector List", "Velocities", "velocities")
        self.newInput("Quaternion List", "Rotations", "rotations")
        self.newInput("Float List", "Die Times", "dietimes")
        
        self.updateSocketVisibility()

    def updateSocketVisibility(self):
        self.inputs[1].hide = not self.locBool
        self.inputs[2].hide = not self.velBool
        self.inputs[3].hide = not self.rotBool
        self.inputs[4].hide = not self.dieBool

    def execute(self, particleSystem, locations, velocities, rotations, dietimes):
        if object is None or particleSystem is None:
            return   
        particles = particleSystem.particles
        if len(locations) != 0 and self.locBool: particles.foreach_set('location', self.flatList(locations))
        if len(velocities) != 0 and self.velBool: particles.foreach_set('velocity', self.flatList(velocities))
        if len(rotations) != 0 and self.rotBool: particles.foreach_set('rotation', self.flatList(rotations))
        if len(dietimes) != 0 and self.dieBool: particles.foreach_set('die_time', dietimes)
            
    def flatList(self, vectors):
        return list(chain.from_iterable(vectors))
