import bpy
from ... base_types.node import AnimationNode

class TransformSpline(bpy.types.Node, AnimationNode):
    bl_idname = "an_TransformSpline"
    bl_label = "Transform Spline"

    inputNames = { "Spline" : "spline",
                   "Transformation" : "transformation" }

    outputNames = { "Spline" : "spline" }

    def create(self):
        self.inputs.new("an_SplineSocket", "Spline").showName = False
        self.inputs.new("an_MatrixSocket", "Transformation")
        self.outputs.new("an_SplineSocket", "Spline")

    def execute(self, spline, transformation):
        spline.transform(transformation)
        spline.isChanged = True
        return spline
