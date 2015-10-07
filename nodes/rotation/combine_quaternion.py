import bpy
from ... base_types.node import AnimationNode

class CombineQuaternionNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_CombineQuaternionNode"
    bl_label = "Combine Quaternion"

    def create(self):
        self.inputs.new("an_FloatSocket", "W", "w").value = 1
        self.inputs.new("an_FloatSocket", "X", "x")
        self.inputs.new("an_FloatSocket", "Y", "y")
        self.inputs.new("an_FloatSocket", "Z", "z")
        self.outputs.new("an_QuaternionSocket", "Quaternion", "quaternion")

    def getExecutionCode(self):
        return "quaternion = mathutils.Quaternion((w, x, y, z))"

    def getUsedModules(self):
        return ["mathutils"]
