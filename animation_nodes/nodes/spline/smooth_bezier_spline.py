import bpy
from ... base_types import AnimationNode

class SmoothBezierSplineNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SmoothBezierSplineNode"
    bl_label = "Smooth Bezier Spline"

    def create(self):
        socket = self.newInput("Spline", "Spline", "spline")
        socket.showObjectInput = False
        socket.dataIsModified = True
        self.newInput("Float", "Smoothness", "smoothness", value = 0.3333)
        self.newOutput("Spline", "Spline", "outSpline")

    def execute(self, spline, smoothness):
        if spline.type == "BEZIER":
            spline.calculateSmoothHandles(smoothness)
            spline.markChanged()
        return spline
