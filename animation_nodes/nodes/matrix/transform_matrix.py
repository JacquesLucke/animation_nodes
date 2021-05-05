import bpy
from ... base_types import AnimationNode, VectorizedSocket

class TransformMatrixNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_TransformMatrixNode"
    bl_label = "Transform Matrix"

    useMatrixList: VectorizedSocket.newProperty()
    useTransformList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("Matrix", "useMatrixList",
            ("Matrix", "inMatrix"), ("Matrices", "inMatrices")))

        self.newInput(VectorizedSocket("Matrix", "useTransformList",
            ("Transformation", "transformation"),
            ("Transformations", "transformations")))

        self.newOutput(VectorizedSocket("Matrix", ["useMatrixList", "useTransformList"],
            ("Matrix", "outMatrix"), ("Matrices", "outMatrices")))

    def getExecutionCode(self, required):
        if any((self.useMatrixList, self.useTransformList)):
            if not self.useMatrixList: yield "inMatrices = Matrix4x4List.fromValue(inMatrix)"
            if not self.useTransformList: yield "transformations = Matrix4x4List.fromValue(transformation)"
            yield "_inMatrices = VirtualMatrix4x4List.create(inMatrices, Matrix.Identity(4))"
            yield "_transformations = VirtualMatrix4x4List.create(transformations, Matrix.Identity(4))"
            yield "amount = VirtualMatrix4x4List.getMaxRealLength(_inMatrices, _transformations)"
            yield "outMatrices = AN.nodes.matrix.c_utils.transformVirtualMatrix4x4List(amount, _inMatrices, _transformations)"
        else:
            yield "outMatrix = transformation @ inMatrix"
