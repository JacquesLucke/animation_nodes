import bpy
from bpy.props import *
from ... base_types import VectorizedNode
from ... math cimport setTranslationMatrix
from ... data_structures cimport Matrix4x4List, Vector3DList

class TranslationMatrixNode(bpy.types.Node, VectorizedNode):
    bl_idname = "an_TranslationMatrixNode"
    bl_label = "Translation Matrix"

    useList = VectorizedNode.newVectorizeProperty()

    def createVectorized(self):
        self.newVectorizedInput("Vector", "useList",
            ("Translation", "translation"), ("Translations", "translations"))

        self.newVectorizedOutput("Matrix", "useList",
            ("Matrix", "matrix"), ("Matrices", "matrices"))

    def getExecutionCode(self):
        if self.useList:
            return "matrices = self.calcMatrices(translations)"
        else:
            return "matrix = Matrix.Translation(translation)"

    def calcMatrices(self, Vector3DList vectors):
        cdef Matrix4x4List matrices = Matrix4x4List(length = vectors.length)
        cdef size_t i
        for i in range(vectors.length):
            setTranslationMatrix(matrices.data + i, vectors.data + i)
        return matrices
