import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode

directionAxisItems = [(axis, axis, "") for axis in ("X", "Y", "Z", "-X", "-Y", "-Z")]

class RotationToDirectionNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_RotationToDirectionNode"
    bl_label = "Rotation to Direction"
    bl_width_default = 160

    directionAxis = EnumProperty(items = directionAxisItems, update = propertyChanged, default = "Z")

    def create(self):
        self.newInput("Euler", "Rotation", "rotation")
        self.newInput("Float", "Length", "length", value = 1)
        self.newOutput("Vector", "Direction", "direction")

    def draw(self, layout):
        layout.prop(self, "directionAxis", expand = True)

    def getExecutionCode(self):
        yield "direction = animation_nodes.algorithms.rotation.rotationToDirection(rotation, self.directionAxis)"
        yield "direction *= length"
