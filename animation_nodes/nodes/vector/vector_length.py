import bpy
from ... base_types import AnimationNode, VectorizedSocket
from . c_utils import calculateVectorLengths

class VectorLengthNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_VectorLengthNode"
    bl_label = "Vector Length"

    useList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("Vector", "useList",
            ("Vector", "vector"), ("Vectors", "vectors")))

        self.newOutput(VectorizedSocket("Float", "useList",
            ("Length", "length"), ("Lenghts", "lengths")))

    def getExecutionCode(self, required):
        if self.useList:
            yield "lengths = self.calcLengths(vectors)"
        else:
            yield "length = vector.length"

    def calcLengths(self, vectors):
        return calculateVectorLengths(vectors)
