import bpy
from ... base_types.node import AnimationNode

class VectorFromValueNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_VectorFromValueNode"
    bl_label = "Vector from Value"

    def create(self):
        self.inputs.new("an_FloatSocket", "Value", "value")
        self.outputs.new("an_VectorSocket", "Vector", "vector")

    def getExecutionCode(self):
        return "vector = mathutils.Vector((value, value, value))"

    def getModuleList(self):
        return ["mathutils"]
