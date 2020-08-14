import bpy
from bpy.props import *
from ... events import propertyChanged
from ... data_structures import Matrix4x4List
from ... base_types import AnimationNode, VectorizedSocket
from . c_utils import extractMatricesXBasis, extractMatricesYBasis, extractMatricesZBasis

basisAxisItems = [
    ("X", "X", "", "NONE", 0),
    ("Y", "Y", "", "NONE", 1),
    ("Z", "Z", "", "NONE", 2)
]

class ExtractMatrixBasisNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ExtractMatrixBasisNode"
    bl_label = "Extract Matrix Basis"

    basisAxis: EnumProperty(name = "Axis", default = "X",
        items = basisAxisItems, update = propertyChanged)

    useMatrixList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("Matrix", "useMatrixList",
            ("Matrix", "matrix"), ("Matrices", "matrices")))
        self.newOutput(VectorizedSocket("Vector", "useMatrixList",
            ("Basis", "basis"), ("Bases", "bases")))

    def draw(self, layout):
        layout.prop(self, "basisAxis", text = "")

    def execute(self, matrices):
        if not self.useMatrixList:
            matrices = Matrix4x4List.fromValue(matrices)

        if self.basisAxis == 'X':
            bases = extractMatricesXBasis(matrices)
        elif self.basisAxis == 'Y':
            bases = extractMatricesYBasis(matrices)
        elif self.basisAxis == 'Z':
            bases = extractMatricesZBasis(matrices)

        if not self.useMatrixList:
            return bases[0]
        else:
            return bases
