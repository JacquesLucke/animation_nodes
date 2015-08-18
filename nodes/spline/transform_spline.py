import bpy
from ... base_types.node import AnimationNode

class TransformSpline(bpy.types.Node, AnimationNode):
    bl_idname = "an_TransformSpline"
    bl_label = "Transform Spline"

    def create(self):
        self.inputs.new("an_SplineSocket", "Spline", "spline").showName = False
        self.inputs.new("an_MatrixSocket", "Transformation", "matrix")
        self.outputs.new("an_SplineSocket", "Spline", "outSpline")

    def execute(self, spline, matrix):
        spline.transform(matrix)
        spline.isChanged = True
        return spline
