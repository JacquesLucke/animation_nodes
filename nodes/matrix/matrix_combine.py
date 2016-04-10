import bpy
import operator
import functools
from mathutils import Matrix
from ... base_types.node import AnimationNode

class MatrixCombineNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MatrixCombineNode"
    bl_label = "Combine Matrices"

    def create(self):
        self.newInput("an_MatrixListSocket", "Matrices", "matrices")
        self.newOutput("an_MatrixSocket", "Result", "result")

    def execute(self, matrices):
        return functools.reduce(operator.mul, reversed(matrices), Matrix.Identity(4))
