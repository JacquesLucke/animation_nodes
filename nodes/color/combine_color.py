import bpy, random
from ... base_types.node import AnimationNode


class CombineColor(bpy.types.Node, AnimationNode):
    bl_idname = "an_CombineColor"
    bl_label = "Combine Color"
    isDetermined = True

    def create(self):
        self.inputs.new("an_FloatSocket", "Red", "red")
        self.inputs.new("an_FloatSocket", "Green", "green")
        self.inputs.new("an_FloatSocket", "Blue", "blue")
        self.inputs.new("an_FloatSocket", "Alpha", "alpha").value = 1
        self.outputs.new("an_ColorSocket", "Color", "color")

    def execute(self, red, green, blue, alpha):
        return [red, green, blue, alpha]
