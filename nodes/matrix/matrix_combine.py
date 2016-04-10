import bpy
import operator
import functools
from mathutils import Matrix
from ... base_types.node import AnimationNode

class MatrixCombineNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MatrixCombineNode"
    bl_label = "Combine Matrices"

    def create(self):
        self.newInput("Matrix List", "Matrices", "matrices")
        self.newOutput("Matrix", "Result", "result")

    def execute(self, matrices):
        return functools.reduce(operator.mul, reversed(matrices), Matrix.Identity(4))
