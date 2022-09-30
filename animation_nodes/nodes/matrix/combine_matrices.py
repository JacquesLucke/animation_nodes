import bpy
from ... base_types import AnimationNode
from . c_utils import reduceMatrixList

class MatrixCombineNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_MatrixCombineNode"
    bl_label = "Combine Matrices"

    def create(self):
        self.newInput("Matrix List", "Matrices", "matrices")
        self.newOutput("Matrix", "Result", "result")

    def execute(self, matrices):
        return reduceMatrixList(matrices, reversed = True)
