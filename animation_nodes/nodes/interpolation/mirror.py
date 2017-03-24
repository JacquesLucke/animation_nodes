import bpy
from ... base_types import AnimationNode
from ... algorithms.interpolations import MirrorInterpolation

class MirrorInterpolationNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MirrorInterpolationNode"
    bl_label = "Mirror Interpolation"

    def create(self):
        self.newInput("Interpolation", "Interpolation", "interpolationIn", defaultDrawType = "PROPERTY_ONLY")
        self.newOutput("Interpolation", "Interpolation", "interpolationOut")

    def execute(self, interpolation):
        return MirrorInterpolation(interpolation)
