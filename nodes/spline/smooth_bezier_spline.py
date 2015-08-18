import bpy
from ... base_types.node import AnimationNode

class SmoothBezierSpline(bpy.types.Node, AnimationNode):
    bl_idname = "an_SmoothBezierSpline"
    bl_label = "Smooth Bezier Spline"

    def create(self):
        self.inputs.new("an_SplineSocket", "Spline", "spline").showObjectInput = False
        self.inputs.new("an_FloatSocket", "Smoothness", "smoothness").value = 0.3333
        self.outputs.new("an_SplineSocket", "Spline", "outSpline")

    def execute(self, spline, smoothness):
        if spline.type == "BEZIER":
            spline.calculateSmoothHandles(smoothness)
            spline.isChanged = True
        return spline
