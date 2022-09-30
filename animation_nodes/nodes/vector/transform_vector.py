import bpy
from ... base_types import AnimationNode, VectorizedSocket

class TransformVectorNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_TransformVectorNode"
    bl_label = "Transform Vector"

    useVectorList: VectorizedSocket.newProperty()
    useMatrixList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("Vector", "useVectorList",
            ("Vector", "vector"), ("Vectors", "vectors")))
        self.newInput(VectorizedSocket("Matrix", "useMatrixList",
            ("Matrix", "matrix"), ("Matrices", "matrices")))

        self.newOutput(VectorizedSocket("Vector", ["useVectorList", "useMatrixList"],
            ("Vector", "transformedVector"), ("Vectors", "vectors")))

    def getExecutionCode(self, required):
        if any((self.useVectorList, self.useMatrixList)):
            if not self.useVectorList: yield "vectors = Vector3DList.fromValue(vector)"
            if not self.useMatrixList: yield "matrices = Matrix4x4List.fromValue(matrix)"
            yield "_vectors = VirtualVector3DList.create(vectors, (0,0,0))"
            yield "_matrices = VirtualMatrix4x4List.create(matrices, Matrix.Identity(4))"
            yield "amount = VirtualVector3DList.getMaxRealLength(_vectors, _matrices)"
            yield "vectors = AN.nodes.vector.c_utils.transformVirtualVectorList(amount, _vectors, _matrices)"
        else:
            yield "transformedVector = matrix @ vector"
