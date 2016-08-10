import bpy
from ... base_types.node import AnimationNode

class SplineInfoNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SplineInfoNode"
    bl_label = "Spline Info"

    def create(self):
        self.newInput("Spline", "Spline", "spline", defaultDrawType = "PROPERTY_ONLY")
        self.newOutput("Boolean", "Cyclic", "cyclic")

    def execute(self, spline):
        return spline.cyclic
