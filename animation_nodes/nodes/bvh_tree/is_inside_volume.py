import bpy
from ... base_types import AnimationNode, VectorizedSocket

class IsInsideVolumeBVHTreeNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_IsInsideVolumeBVHTreeNode"
    bl_label = "Is Inside Volume"
    codeEffects = [VectorizedSocket.CodeEffect]

    useVectorList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput("BVHTree", "BVHTree", "bvhTree", defaultDrawType = "PROPERTY_ONLY")

        self.newInput(VectorizedSocket("Vector", "useVectorList",
            ("Vector", "vector", dict(defaultDrawType = "PROPERTY_ONLY")),
            ("Vectors", "vectors", dict(defaultDrawType = "PROPERTY_ONLY"))))

        self.newOutput(VectorizedSocket("Boolean", "useVectorList",
            ("Is Inside", "isInside"), ("Are Inside", "areInside")))

    def getExecutionCode(self, required):
        return "isInside = AN.utils.bvh.isInsideVolume(bvhTree, vector)"
