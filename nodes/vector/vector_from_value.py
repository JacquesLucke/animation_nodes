import bpy
from ... base_types.node import AnimationNode

class VectorFromValueNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_VectorFromValueNode"
    bl_label = "Vector from Value"

    def create(self):
        self.newInput("an_FloatSocket", "Value", "value")
        self.newOutput("an_VectorSocket", "Vector", "vector")

    def getExecutionCode(self):
        return "vector = mathutils.Vector((value, value, value))"

    def getUsedModules(self):
        return ["mathutils"]
