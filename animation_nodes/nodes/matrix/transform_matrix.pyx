import bpy
from bpy.props import *
from ... data_structures cimport Matrix4x4List
from ... math cimport multMatrix4, Matrix4, toMatrix4
from ... base_types import AnimationNode, AutoSelectVectorization

class TransformMatrixNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_TransformMatrixNode"
    bl_label = "Transform Matrix"

    useMatrixList = BoolProperty(update = AnimationNode.refresh)

    def create(self):
        self.newInputGroup(self.useMatrixList,
            ("Matrix", "Matrix", "inMatrix"),
            ("Matrix List", "Matrices", "inMatrices"))

        self.newInput("Matrix", "Transformation", "transformation")

        self.newOutputGroup(self.useMatrixList,
            ("Matrix", "Matrix", "outMatrix"),
            ("Matrix List", "Matrices", "outMatrices"))

        vectorization = AutoSelectVectorization()
        vectorization.input(self, "useMatrixList", self.inputs[0])
        vectorization.output(self, "useMatrixList", self.outputs[0])
        self.newSocketEffect(vectorization)

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
