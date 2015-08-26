import bpy
from ... base_types.node import AnimationNode
from ... algorithms.interpolation import mixedInterpolation

class MixInterpolation(bpy.types.Node, AnimationNode):
    bl_idname = "an_MixInterpolation"
    bl_label = "Mix Interpolation"

    def create(self):
        self.inputs.new("an_FloatSocket", "Factor", "factor").setMinMax(0, 1)
        self.inputs.new("an_InterpolationSocket", "Interpolation 1", "a").showName = False
        self.inputs.new("an_InterpolationSocket", "Interpolation 2", "b").showName = False
        self.outputs.new("an_InterpolationSocket", "Interpolation", "interpolation")

    def execute(self, factor, a, b):
        return (mixedInterpolation, (a, b, factor))
