import bpy
from ... utils.bvh import isInsideVolume
from ... base_types import AnimationNode, VectorizedSocket

class IsInsideVolumeBVHTreeNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_IsInsideVolumeBVHTreeNode"
    bl_label = "Is Inside Volume"
    codeEffects = [VectorizedSocket.CodeEffect]

    useVectorList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput("BVHTree", "BVHTree", "bvhTree")

        self.newInput(VectorizedSocket("Vector", "useVectorList",
            ("Vector", "vector", dict(defaultDrawType = "PROPERTY_ONLY")),
            ("Vectors", "vectors", dict(defaultDrawType = "PROPERTY_ONLY"))))

        self.newOutput(VectorizedSocket("Boolean", "useVectorList",
            ("Is Inside", "isInside"), ("Are Inside", "areInside")))

    def getExecutionCode(self, required):
        return "isInside = self.execute_Single(bvhTree, vector)"

    def execute_Single(self, bvhTree, vector):
        return isInsideVolume(bvhTree, vector)
