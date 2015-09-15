import bpy
from ... base_types.node import AnimationNode
from ... algorithms.interpolation import mixedInterpolation

class MixInterpolationNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MixInterpolationNode"
    bl_label = "Mix Interpolation"

    def create(self):
        self.inputs.new("an_FloatSocket", "Factor", "factor").setRange(0, 1)
        self.inputs.new("an_InterpolationSocket", "Interpolation 1", "a").defaultDrawType = "PROPERTY_ONLY"
        self.inputs.new("an_InterpolationSocket", "Interpolation 2", "b").defaultDrawType = "PROPERTY_ONLY"
        self.outputs.new("an_InterpolationSocket", "Interpolation", "interpolation")

    def execute(self, factor, a, b):
        return (mixedInterpolation, (a, b, factor))
