import bpy
import itertools
from bpy.props import *
from ... events import isRendering
from mathutils.bvhtree import BVHTree
from ... tree_info import keepNodeState
from ... base_types.node import AnimationNode

sourceTypeItems = [
    ("MESH_DATA", "Mesh Data", "", "", 0),
    ("BMESH", "BMesh", "", "", 1) ]

class ConstructBVHTreeNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ConstructBVHTreeNode"
    bl_label = "Construct BVHTree"
    bl_width_default = 160

    def sourceTypeChanged(self, context):
        self.recreateInputs()

    sourceType = EnumProperty(name = "Source Type", default = "MESH_DATA",
        items = sourceTypeItems, update = sourceTypeChanged)

    def create(self):
        self.recreateInputs()
        self.outputs.new("an_BVHTreeSocket", "BVHTree", "bvhTree")

    def draw(self, layout):
        layout.prop(self, "sourceType", text = "Source")

    @keepNodeState
    def recreateInputs(self):
        self.inputs.clear()

        if self.sourceType == "MESH_DATA":
            self.inputs.new("an_VectorListSocket", "Vector List", "vectorList")
            self.inputs.new("an_PolygonIndicesListSocket", "Polygon Indices", "polygonsIndices")
        elif self.sourceType == "BMESH":
            self.inputs.new("an_BMeshSocket", "BMesh", "bm")

        socket = self.inputs.new("an_FloatSocket", "Epsilon", "epsilon")
        socket.hide = True
        socket.minValue = 0.0

    def getExecutionCode(self):
        if self.sourceType == "MESH_DATA":
            return "bvhTree = self.fromMeshData(vectorList, polygonsIndices, max(epsilon, 0))"
        elif self.sourceType == "BMESH":
            return "bvhTree = self.fromBMesh(bm, max(epsilon, 0))"

    def getUsedModules(self):
        return ["mathutils"]

    def fromMeshData(self, vectorList, polygonsIndices, epsilon):
        maxPolygonIndex = max(itertools.chain([-1], *polygonsIndices))
        minPolygonIndex = min(itertools.chain([0], *polygonsIndices))

        if 0 <= minPolygonIndex and maxPolygonIndex < len(vectorList):
            return BVHTree.FromPolygons(vectorList, polygonsIndices, epsilon = epsilon)
        return BVHTree.FromPolygons([], [], epsilon = epsilon)

    def fromBMesh(self, bm, epsilon):
        return BVHTree.FromBMesh(bm, epsilon = epsilon)
