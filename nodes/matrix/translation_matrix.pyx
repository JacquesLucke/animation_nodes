import bpy
from ... sockets.info import isList
from ... math cimport setTranslationMatrix
from ... data_structures cimport Matrix4x4List, Vector3DList
from ... base_types import AnimationNode, DynamicSocketSet

class DynamicSockets(DynamicSocketSet):
    def defaults(self):
        self.newInput("Vector", "Translation", "translation")
        self.newOutput("Matrix", "Matrix", "matrix")

    def states(self, inputs, outputs):
        self.setState(inputs[0], "Vector List", "Translations", "translations")
        self.setState(outputs[0], "Matrix List", "Matrices", "matrices")

    def rules(self, inputs, outputs):
        if inputs[0].isLinkedToType("Vector List") or outputs[0].isLinkedToType("Matrix List"):
            self.setType(inputs[0], "Vector List")
            self.setType(outputs[0], "Matrix List")

socketSet = DynamicSockets()

class TranslationMatrixNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_TranslationMatrixNode"
    bl_label = "Translation Matrix"

    def create(self):
        socketSet.createDefaults(self)

    def edit(self):
        socketSet.applyRules(self)

    def getExecutionCode(self):
        if isList(self.inputs[0].dataType):
            return "matrices = self.calcMatrices(translations)"
        else:
            return "matrix = Matrix.Translation(translation)"

    def calcMatrices(self, Vector3DList vectors):
        cdef Matrix4x4List matrices = Matrix4x4List(length = vectors.length)
        cdef size_t i
        for i in range(vectors.length):
            setTranslationMatrix(matrices.data + i, vectors.data + i)
        return matrices
