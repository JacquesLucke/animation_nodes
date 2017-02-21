import bpy
from bpy.props import *
from mathutils.bvhtree import BVHTree
from ... base_types import AnimationNode

sourceTypeItems = [
    ("MESH_DATA", "Mesh Data", "", "", 0),
    ("BMESH", "BMesh", "", "", 1) ]

class ConstructBVHTreeNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ConstructBVHTreeNode"
    bl_label = "Construct BVHTree"
    bl_width_default = 160

    sourceType = EnumProperty(name = "Source Type", default = "MESH_DATA",
        items = sourceTypeItems, update = AnimationNode.refresh)

    def create(self):
        if self.sourceType == "MESH_DATA":
            self.newInput("Vector List", "Vector List", "vectorList")
            self.newInput("Polygon Indices List", "Polygon Indices", "polygonsIndices")
        elif self.sourceType == "BMESH":
            self.newInput("BMesh", "BMesh", "bm")
        self.newInput("Float", "Epsilon", "epsilon", hide = True, minValue = 0)
        self.newOutput("BVHTree", "BVHTree", "bvhTree")

    def draw(self, layout):
        layout.prop(self, "sourceType", text = "Source")

    def getExecutionCode(self):
        if self.sourceType == "MESH_DATA":
            return "bvhTree = self.fromMeshData(vectorList, polygonsIndices, max(epsilon, 0))"
        elif self.sourceType == "BMESH":
            return "bvhTree = self.fromBMesh(bm, max(epsilon, 0))"

    def getUsedModules(self):
        return ["mathutils"]

    def fromMeshData(self, vectorList, polygonsIndices, epsilon):
        if len(polygonsIndices) > 0:
            if 0 <= polygonsIndices.getMinIndex() <= polygonsIndices.getMaxIndex() < len(vectorList):
                return BVHTree.FromPolygons(vectorList, polygonsIndices, epsilon = epsilon)
        return BVHTree.FromPolygons([], [], epsilon = epsilon)

    def fromBMesh(self, bm, epsilon):
        return BVHTree.FromBMesh(bm, epsilon = epsilon)
