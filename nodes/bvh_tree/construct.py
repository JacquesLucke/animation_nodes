import bpy
import itertools
from mathutils.bvhtree import BVHTree
from ... base_types.node import AnimationNode

class ConstructBVHTreeNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ConstructBVHTreeNode"
    bl_label = "Construct BVHTree"

    def create(self):
        self.inputs.new("an_VectorListSocket", "Vector List", "vectorList")
        self.inputs.new("an_PolygonIndicesListSocket", "Polygon Indices", "polygonsIndices")
        self.outputs.new("an_BVHTreeSocket", "BVHTree", "bvhTree")

    def execute(self, vectorList, polygonsIndices):
        maxPolygonIndex = max(itertools.chain([-1], *polygonsIndices))
        minPolygonIndex = min(itertools.chain([0], *polygonsIndices))

        if 0 <= minPolygonIndex and maxPolygonIndex < len(vectorList):
            return BVHTree.FromPolygons(vectorList, polygonsIndices)
        return BVHTree.FromPolygons([], [])
