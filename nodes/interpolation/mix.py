import bpy
from ... base_types.node import AnimationNode
from ... algorithms.interpolations import Mixed

class MixInterpolationNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MixInterpolationNode"
    bl_label = "Mix Interpolation"

    def create(self):
        self.newInput("Float", "Factor", "factor").setRange(0, 1)
        self.newInput("Interpolation", "Interpolation 1", "a", defaultDrawType = "PROPERTY_ONLY")
        self.newInput("Interpolation", "Interpolation 2", "b", defaultDrawType = "PROPERTY_ONLY")
        self.newOutput("Interpolation", "Interpolation", "interpolation")

    def execute(self, factor, a, b):
        return Mixed(factor, a, b)
