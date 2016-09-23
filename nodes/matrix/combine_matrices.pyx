import bpy
from ... base_types import AnimationNode
from ... data_structures cimport Matrix4x4List
from ... math cimport reduceMatrix4x4List, toPyMatrix4, Matrix4

class MatrixCombineNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MatrixCombineNode"
    bl_label = "Combine Matrices"

    def create(self):
        self.newInput("Matrix List", "Matrices", "matrices")
        self.newOutput("Matrix", "Result", "result")

    def execute(self, Matrix4x4List matrices):
        cdef Matrix4 result
        reduceMatrix4x4List(matrices.data, matrices.length, &result, reversed = True)
        return toPyMatrix4(&result)
