import bpy
import operator
import functools
from mathutils import Quaternion
from ... base_types import AnimationNode

class QuaternionListCombineNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_QuaternionListCombineNode"
    bl_label = "Combine Quaternion Rotations"

    def create(self):
        self.newInput("Quaternion List", "Quaternions", "quaternions")
        self.newOutput("Quaternion", "Result", "result")

    def execute(self, quaternions):
        return functools.reduce(operator.matmul, reversed(quaternions), Quaternion((1, 0, 0, 0)))
