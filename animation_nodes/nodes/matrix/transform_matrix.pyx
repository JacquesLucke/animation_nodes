import bpy
from bpy.props import *
from ... base_types import VectorizedNode
from ... data_structures cimport Matrix4x4List
from ... math cimport multMatrix4, Matrix4, toMatrix4

class TransformMatrixNode(bpy.types.Node, VectorizedNode):
    bl_idname = "an_TransformMatrixNode"
    bl_label = "Transform Matrix"

    useMatrixList = VectorizedNode.newVectorizeProperty()

    def create(self):
        self.newVectorizedInput("Matrix", "useMatrixList",
            ("Matrix", "inMatrix"), ("Matrices", "inMatrices"))

        self.newInput("Matrix", "Transformation", "transformation")

        self.newVectorizedOutput("Matrix", "useMatrixList",
            ("Matrix", "outMatrix"), ("Matrices", "outMatrices"))

    def getExecutionFunctionName(self):
        if self.useMatrixList:
            return "execute_MatrixList"
        else:
            return "execute_Matrix"

    def execute_Matrix(self, inMatrix, transformation):
        return transformation * inMatrix

    def execute_MatrixList(self, Matrix4x4List inMatrices, _transformation):
        cdef Matrix4 transformation = toMatrix4(_transformation)
        cdef Matrix4x4List outMatrices = Matrix4x4List(length = len(inMatrices))
        cdef long i
        for i in range(len(outMatrices)):
            multMatrix4(outMatrices.data + i, &transformation, inMatrices.data + i)
        return outMatrices
