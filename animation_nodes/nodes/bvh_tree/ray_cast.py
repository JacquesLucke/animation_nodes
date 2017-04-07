import bpy
import sys
from ... base_types import VectorizedNode

class RayCastBVHTreeNode(bpy.types.Node, VectorizedNode):
    bl_idname = "an_RayCastBVHTreeNode"
    bl_label = "Ray Cast BVHTree"
    bl_width_default = 150
    autoVectorizeExecution = True

    useStartList = VectorizedNode.newVectorizeProperty()
    useDirectionList = VectorizedNode.newVectorizeProperty()

    def create(self):
        self.newInput("BVHTree", "BVHTree", "bvhTree")

        self.newVectorizedInput("Vector", "useStartList",
            ("Ray Start", "start"), ("Ray Starts", "starts"))
        self.newVectorizedInput("Vector", "useDirectionList",
            ("Ray Direction", "direction"), ("Ray Directions", "directions"))

        self.newInput("Float", "Min Distance", "minDistance", value = 0.001, hide = True)
        self.newInput("Float", "Max Distance", "maxDistance", value = 1e6, hide = True)

        useListOutput = [("useStartList", "useDirectionList")]

        self.newVectorizedOutput("Vector", useListOutput,
            ("Location", "location"), ("Locations", "locations"))
        self.newVectorizedOutput("Vector", useListOutput,
            ("Normal", "normal"), ("Normals", "normals"))
        self.newVectorizedOutput("Float", useListOutput,
            ("Distance", "distance"), ("Distances", "distances"))
        self.newVectorizedOutput("Integer", useListOutput,
            ("Polygon Index", "polygonIndex", dict(hide = True)),
            ("Polygon Indices", "polygonIndices", dict(hide = True)))
        self.newVectorizedOutput("Boolean", useListOutput,
            ("Hit", "hit"), ("Hits", "hits"))

    def getExecutionCode(self):
        yield "location, normal, polygonIndex, distance = bvhTree.ray_cast(start + direction.normalized() * minDistance, direction, maxDistance - minDistance)"
        yield "if location is None:"
        yield "    location = Vector((0, 0, 0))"
        yield "    polygonIndex = -1"
        yield "    normal = Vector((0, 0, 0))"
        yield "    distance = 0"
        yield "    hit = False"
        yield "else: hit = True"
