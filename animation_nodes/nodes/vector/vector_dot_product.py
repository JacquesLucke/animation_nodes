import bpy
from . c_utils import calculateVectorDotProducts
from ... data_structures import VirtualVector3DList
from ... base_types import AnimationNode, VectorizedSocket

class VectorDotProductNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_VectorDotProductNode"
    bl_label = "Vector Dot Product"

    useListA: VectorizedSocket.newProperty()
    useListB: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("Vector", "useListA",
            ("A", "a"), ("A", "a")))
        self.newInput(VectorizedSocket("Vector", "useListB",
            ("B", "b"), ("B", "b")))

        self.newOutput(VectorizedSocket("Float", ["useListA", "useListB"],
            ("Dot Product", "dotProduct"), ("Dot Product", "dotProducts")))

    def getExecutionCode(self, required):
        if self.useListA or self.useListB:
            yield "dotProducts = self.calculateDotProducts(a, b)"
        else:
            yield "distance = (a - b).length"
            yield "dotProduct = a.dot(b)"

    def calculateDotProducts(self, a, b):
        vectors1 = VirtualVector3DList.create(a, (0, 0, 0))
        vectors2 = VirtualVector3DList.create(b, (0, 0, 0))
        return calculateVectorDotProducts(vectors1, vectors2)
