import bpy
from ... base_types.node import AnimationNode

class SmoothBezierSpline(bpy.types.Node, AnimationNode):
    bl_idname = "an_SmoothBezierSpline"
    bl_label = "Smooth Bezier Spline"

    inputNames = { "Spline" : "spline",
                   "Smoothness" : "smoothness" }

    outputNames = { "Spline" : "spline" }

    def create(self):
        self.inputs.new("an_SplineSocket", "Spline").showObjectInput = False
        self.inputs.new("an_FloatSocket", "Smoothness").value = 0.3333
        self.outputs.new("an_SplineSocket", "Spline")

    def execute(self, spline, smoothness):
        if spline.type == "BEZIER":
            spline.calculateSmoothHandles(smoothness)
            spline.isChanged = True
        return spline
