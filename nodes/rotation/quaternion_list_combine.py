import bpy
import operator
import functools
from mathutils import Quaternion
from ... base_types.node import AnimationNode

class QuaternionListCombineNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_QuaternionListCombineNode"
    bl_label = "Combine Quaternion Rotations"

    def create(self):
        self.newInput("an_QuaternionListSocket", "Quaternions", "quaternions")
        self.newOutput("an_QuaternionSocket", "Result", "result")

    def execute(self, quaternions):
        return functools.reduce(operator.mul, reversed(quaternions), Quaternion((1, 0, 0, 0)))
