import bpy
from ... base_types.node import AnimationNode

class TransformSpline(bpy.types.Node, AnimationNode):
    bl_idname = "mn_TransformSpline"
    bl_label = "Transform Spline"

    inputNames = { "Spline" : "spline",
                   "Transformation" : "transformation" }

    outputNames = { "Spline" : "spline" }

    def create(self):
        self.inputs.new("mn_SplineSocket", "Spline").showName = False
        self.inputs.new("mn_MatrixSocket", "Transformation")
        self.outputs.new("mn_SplineSocket", "Spline")

    def execute(self, spline, transformation):
        spline.transform(transformation)
        spline.isChanged = True
        return spline
