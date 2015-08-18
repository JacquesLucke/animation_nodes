import bpy
import operator
import functools
from mathutils import Matrix
from ... base_types.node import AnimationNode

class MatrixCombine(bpy.types.Node, AnimationNode):
    bl_idname = "an_MatrixCombine"
    bl_label = "Combine Matrices"
    isDetermined = True

    def create(self):
        self.inputs.new("an_MatrixListSocket", "Matrices", "matrices")
        self.outputs.new("an_MatrixSocket", "Result", "result")

    def execute(self, matrices):
        return functools.reduce(operator.mul, reversed(matrices), Matrix.Identity(4))
