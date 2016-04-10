import bpy
from ... base_types.node import AnimationNode
from ... algorithms.interpolation import mixedInterpolation, assignArguments

class MixInterpolationNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MixInterpolationNode"
    bl_label = "Mix Interpolation"

    def create(self):
        self.newInput("an_FloatSocket", "Factor", "factor").setRange(0, 1)
        self.newInput("an_InterpolationSocket", "Interpolation 1", "a").defaultDrawType = "PROPERTY_ONLY"
        self.newInput("an_InterpolationSocket", "Interpolation 2", "b").defaultDrawType = "PROPERTY_ONLY"
        self.newOutput("an_InterpolationSocket", "Interpolation", "interpolation")

    def execute(self, factor, a, b):
        return assignArguments(mixedInterpolation, (a, b, factor))
