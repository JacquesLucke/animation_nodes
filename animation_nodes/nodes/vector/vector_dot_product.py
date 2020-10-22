import bpy
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
            yield "_vA = VirtualVector3DList.create(a, (0, 0, 0))"
            yield "_vB = VirtualVector3DList.create(b, (0, 0, 0))"
            yield "dotProducts = AN.nodes.vector.c_utils.calculateVectorDotProducts(_vA, _vB)"
        else:
            yield "distance = (a - b).length"
            yield "dotProduct = a.dot(b)"
