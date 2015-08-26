import bpy
from ... base_types.node import AnimationNode

class TransformSplineNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_TransformSplineNode"
    bl_label = "Transform Spline"

    def create(self):
        socket = self.inputs.new("an_SplineSocket", "Spline", "spline")
        socket.dataIsModified = True
        socket.showName = False
        self.inputs.new("an_MatrixSocket", "Transformation", "matrix")
        self.outputs.new("an_SplineSocket", "Spline", "outSpline")

    def execute(self, spline, matrix):
        spline.transform(matrix)
        spline.isChanged = True
        return spline
