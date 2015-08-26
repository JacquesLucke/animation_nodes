import bpy
from ... base_types.node import AnimationNode

class SmoothBezierSplineNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SmoothBezierSplineNode"
    bl_label = "Smooth Bezier Spline"

    def create(self):
        socket = self.inputs.new("an_SplineSocket", "Spline", "spline")
        socket.showObjectInput = False
        socket.dataIsModified = True
        self.inputs.new("an_FloatSocket", "Smoothness", "smoothness").value = 0.3333
        self.outputs.new("an_SplineSocket", "Spline", "outSpline")

    def execute(self, spline, smoothness):
        if spline.type == "BEZIER":
            spline.calculateSmoothHandles(smoothness)
            spline.isChanged = True
        return spline
