import bpy
from bpy.props import *
from mathutils.bvhtree import BVHTree
from ... base_types import AnimationNode
from ... utils.depsgraph import getEvaluatedID

sourceTypeItems = [
    ("MESH_DATA", "Mesh", "", "NONE", 0),
    ("BMESH", "BMesh", "", "NONE", 1),
    ("OBJECT", "Object", "", "NONE", 2) ]

class ConstructBVHTreeNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_ConstructBVHTreeNode"
    bl_label = "Construct BVHTree"
    bl_width_default = 160

    sourceType: EnumProperty(name = "Source Type", default = "MESH_DATA",
        items = sourceTypeItems, update = AnimationNode.refresh)

    def create(self):
        if self.sourceType == "MESH_DATA":
            self.newInput("Mesh", "Mesh", "mesh")
        elif self.sourceType == "BMESH":
            self.newInput("BMesh", "BMesh", "bm")
        elif self.sourceType == "OBJECT":
            self.newInput("Object", "Object", "object", defaultDrawType = "PROPERTY_ONLY")

        self.newInput("Float", "Epsilon", "epsilon", hide = True, minValue = 0)
        self.newOutput("BVHTree", "BVHTree", "bvhTree")

    def draw(self, layout):
        layout.prop(self, "sourceType", text = "Source")

    def getExecutionFunctionName(self):
        if self.sourceType == "MESH_DATA":
            return "execute_Mesh"
        elif self.sourceType == "BMESH":
            return "execute_BMesh"
        elif self.sourceType == "OBJECT":
            return "execute_Object"

    def execute_Mesh(self, mesh, epsilon):
        if len(mesh.polygons) == 0:
            return self.getFallbackBVHTree()

        return BVHTree.FromPolygons(mesh.vertices, mesh.polygons, epsilon = max(epsilon, 0))

    def execute_BMesh(self, bm, epsilon):
        return BVHTree.FromBMesh(bm, epsilon = max(epsilon, 0))

    def execute_Object(self, object, epsilon):
        if object is None:
            return self.getFallbackBVHTree()
        if object.type != "MESH":
            return self.getFallbackBVHTree()

        evaluatedObject = getEvaluatedID(object)
        mesh = evaluatedObject.data
        polygons = mesh.an.getPolygonIndices()
        if len(polygons) == 0:
            return self.getFallbackBVHTree()
        vertices = mesh.an.getVertices()
        vertices.transform(evaluatedObject.matrix_world)

        return BVHTree.FromPolygons(vertices, polygons, epsilon = max(epsilon, 0))

    def getFallbackBVHTree(self):
        return self.outputs[0].getDefaultValue()
