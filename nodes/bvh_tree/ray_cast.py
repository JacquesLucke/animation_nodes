import bpy
import sys
from ... base_types.node import AnimationNode

class RayCastBVHTreeNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_RayCastBVHTreeNode"
    bl_label = "Ray Cast BVHTree"

    def create(self):
        self.inputs.new("an_BVHTreeSocket", "BVHTree", "bvhTree")
        self.inputs.new("an_VectorSocket", "Ray Start", "start")
        self.inputs.new("an_VectorSocket", "Ray Direction", "direction")
        socket = self.inputs.new("an_FloatSocket", "Min Distance", "minDistance")
        socket.value = 0.001
        socket.hide = True
        socket = self.inputs.new("an_FloatSocket", "Max Distance", "maxDistance")
        socket.value = 1e6
        socket.hide = True
        self.outputs.new("an_VectorSocket", "Location", "location")
        self.outputs.new("an_VectorSocket", "Normal", "normal")
        self.outputs.new("an_BooleanSocket", "Hit", "hit")

    def getExecutionCode(self):
        yield "location, normal, _, _ = bvhTree.ray_cast(start + direction.normalized() * minDistance, direction, maxDistance - minDistance)"
        yield "if location is None:"
        yield "    location = mathutils.Vector((0, 0, 0))"
        yield "    normal = mathutils.Vector((0, 0, 0))"
        yield "    hit = False"
        yield "else: hit = True"

    def getUsedModules(self):
        return ["mathutils"]
