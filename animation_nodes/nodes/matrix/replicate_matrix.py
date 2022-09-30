import bpy
from bpy.props import *
from ... base_types import AnimationNode, VectorizedSocket
from . c_utils import (
    replicateMatrixAtMatrices,
    replicateMatrixAtVectors,
    replicateMatricesAtMatrices,
    replicateMatricesAtVectors
)

transformationTypeItems = [
    ("MATRIX_LIST", "Matrices", "", "NONE", 0),
    ("VECTOR_LIST", "Vectors", "", "NONE", 1)
]

class ReplicateMatrixNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_ReplicateMatrixNode"
    bl_label = "Replicate Matrix"

    useMatrixList: VectorizedSocket.newProperty()

    transformationType: EnumProperty(name = "Transformation Type", default = "MATRIX_LIST",
        items = transformationTypeItems, update = AnimationNode.refresh)

    def create(self):
        self.newInput(VectorizedSocket("Matrix", "useMatrixList",
            ("Matrix", "inMatrix"), ("Matrices", "inMatrices")))

        if self.transformationType == "MATRIX_LIST":
            self.newInput("Matrix List", "Transformations", "transformations")
        else:
            self.newInput("Vector List", "Transformations", "transformations")

        self.newOutput("Matrix List", "Matrices", "outMatrices")

    def draw(self, layout):
        layout.prop(self, "transformationType", text = "")

    def getExecutionFunctionName(self):
        if self.transformationType == "MATRIX_LIST":
            if self.useMatrixList:
                return "execute_List_Matrices"
            else:
                return "execute_Single_Matrices"
        elif self.transformationType == "VECTOR_LIST":
            if self.useMatrixList:
                return "execute_List_Vectors"
            else:
                return "execute_Single_Vectors"

    def execute_Single_Matrices(self, matrix, transformations):
        return replicateMatrixAtMatrices(matrix, transformations)

    def execute_Single_Vectors(self, matrix, translations):
        return replicateMatrixAtVectors(matrix, translations)

    def execute_List_Matrices(self, matrices, transformations):
        return replicateMatricesAtMatrices(matrices, transformations)

    def execute_List_Vectors(self, matrices, translations):
        return replicateMatricesAtVectors(matrices, translations)
