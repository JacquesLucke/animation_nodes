import bpy
from bpy.props import *
from ... math cimport setTranslationMatrix
from ... data_structures cimport Matrix4x4List, Vector3DList
from ... base_types import AnimationNode, AutoSelectVectorization

class TranslationMatrixNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_TranslationMatrixNode"
    bl_label = "Translation Matrix"

    useList = BoolProperty(default = False, update = AnimationNode.updateSockets)

    def create(self):
        self.newInputGroup(self.useList,
            ("Vector", "Translation", "translation"),
            ("Vector List", "Translations", "translations"))

        self.newOutputGroup(self.useList,
            ("Matrix", "Matrix", "matrix"),
            ("Matrix List", "Matrices", "matrices"))

        vectorization = AutoSelectVectorization()
        vectorization.add(self, "useList", [self.inputs[0], self.outputs[0]])
        self.newSocketEffect(vectorization)

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
