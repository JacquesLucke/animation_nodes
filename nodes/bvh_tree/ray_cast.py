import bpy
import sys
from ... base_types.node import AnimationNode

class RayCastBVHTreeNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_RayCastBVHTreeNode"
    bl_label = "Ray Cast BVHTree"
    bl_width_default = 150

    def create(self):
        self.newInput("BVHTree", "BVHTree", "bvhTree")
        self.newInput("Vector", "Ray Start", "start")
        self.newInput("Vector", "Ray Direction", "direction")
        self.newInput("Float", "Min Distance", "minDistance", value = 0.001, hide = True)
        self.newInput("Float", "Max Distance", "maxDistance", value = 1e6, hide = True)

        self.newOutput("Vector", "Location", "location")
        self.newOutput("Vector", "Normal", "normal")
        self.newOutput("Float", "Distance", "distance")
        self.newOutput("Integer", "Polygon Index", "polygonIndex").hide = True
        self.newOutput("Boolean", "Hit", "hit")

    def getExecutionCode(self):
        yield "location, normal, polygonIndex, distance = bvhTree.ray_cast(start + direction.normalized() * minDistance, direction, maxDistance - minDistance)"
        yield "if location is None:"
        yield "    location = Vector((0, 0, 0))"
        yield "    polygonIndex = -1"
        yield "    normal = Vector((0, 0, 0))"
        yield "    distance = 0"
        yield "    hit = False"
        yield "else: hit = True"
