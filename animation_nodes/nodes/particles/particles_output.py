import bpy
from bpy.props import *
from ... events import propertyChanged
from ... events import executionCodeChanged
from ... base_types import AnimationNode, VectorizedSocket
from ... data_structures import VirtualDoubleList, VirtualVector3DList

class ParticlesOutputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ParticlesOutputNode"
    bl_label = "Particles Output"
    bl_width_default = 180
    errorHandlingType = "EXCEPTION"

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
        particleCount = len(particles)

        if self.locBool:
            if len(locations) < particleCount or len(locations) > particleCount:
                self.raiseErrorMessage("Length of Locations list should be equal to the total number of particles.")

            particles.foreach_set('location', locations.asNumpyArray())

        if self.velBool:
            if len(velocities) < particleCount or len(velocities) > particleCount:
                self.raiseErrorMessage("Length of Velocities list should be equal to the total number of particles.")

            particles.foreach_set('velocity', velocities.asNumpyArray())

        if self.rotBool:
            if len(rotations) < particleCount or len(rotations) > particleCount:
                self.raiseErrorMessage("Length of Rotations list should be equal to the total number of particles.")

            particles.foreach_set('rotation', rotations.asNumpyArray())
        if self.dieBool:
            if len(dietimes) < particleCount or len(dietimes) > particleCount:
                self.raiseErrorMessage("Length of Die Times list should be equal to the total number of particles.")

            particles.foreach_set('die_time', dietimes.asNumpyArray())
