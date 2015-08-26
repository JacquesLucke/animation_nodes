import bpy, random
from ... base_types.node import AnimationNode


class CombineColorNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_CombineColorNode"
    bl_label = "Combine Color"

    def create(self):
        self.inputs.new("an_FloatSocket", "Red", "red")
        self.inputs.new("an_FloatSocket", "Green", "green")
        self.inputs.new("an_FloatSocket", "Blue", "blue")
        self.inputs.new("an_FloatSocket", "Alpha", "alpha").value = 1
        self.outputs.new("an_ColorSocket", "Color", "color")

    def execute(self, red, green, blue, alpha):
        return [red, green, blue, alpha]
