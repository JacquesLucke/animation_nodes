import bpy
from bpy.props import *
from ... events import executionCodeChanged
from ... algorithms.rotation import generateRotationToDirectionCode
from ... base_types.node import AnimationNode

directionAxisItems = [(axis, axis, "") for axis in ("X", "Y", "Z", "-X", "-Y", "-Z")]

class RotationToDirectionNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_RotationToDirectionNode"
    bl_label = "Rotation to Direction"

    directionAxis = EnumProperty(items = directionAxisItems, update = executionCodeChanged, default = "Z")

    def create(self):
        self.inputs.new("an_EulerSocket", "Rotation", "rotation")
        self.inputs.new("an_FloatSocket", "Length", "length").value = 1
        self.outputs.new("an_VectorSocket", "Direction", "direction")
        self.width += 20

    def draw(self, layout):
        layout.prop(self, "directionAxis", expand = True)

    def getExecutionCode(self):
        return generateRotationToDirectionCode("rotation", "length", "direction", self.directionAxis)

    def getUsedModules(self):
        return ["mathutils"]
