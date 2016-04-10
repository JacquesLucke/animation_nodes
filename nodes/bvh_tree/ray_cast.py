import bpy
import sys
from ... base_types.node import AnimationNode

class RayCastBVHTreeNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_RayCastBVHTreeNode"
    bl_label = "Ray Cast BVHTree"
    bl_width_default = 150

    def create(self):
        self.newInput("an_BVHTreeSocket", "BVHTree", "bvhTree")
        self.newInput("an_VectorSocket", "Ray Start", "start")
        self.newInput("an_VectorSocket", "Ray Direction", "direction")
        socket = self.newInput("an_FloatSocket", "Min Distance", "minDistance")
        socket.value = 0.001
        socket.hide = True
        socket = self.newInput("an_FloatSocket", "Max Distance", "maxDistance")
        socket.value = 1e6
        socket.hide = True
        self.newOutput("an_VectorSocket", "Location", "location")
        self.newOutput("an_VectorSocket", "Normal", "normal")
        self.newOutput("an_FloatSocket", "Distance", "distance")
        self.newOutput("an_IntegerSocket", "Polygon Index", "polygonIndex").hide = True
        self.newOutput("an_BooleanSocket", "Hit", "hit")

    def getExecutionCode(self):
        yield "location, normal, polygonIndex, distance = bvhTree.ray_cast(start + direction.normalized() * minDistance, direction, maxDistance - minDistance)"
        yield "if location is None:"
        yield "    location = mathutils.Vector((0, 0, 0))"
        yield "    polygonIndex = -1"
        yield "    normal = mathutils.Vector((0, 0, 0))"
        yield "    distance = 0"
        yield "    hit = False"
        yield "else: hit = True"

    def getUsedModules(self):
        return ["mathutils"]
