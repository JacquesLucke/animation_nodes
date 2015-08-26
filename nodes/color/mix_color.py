import bpy, random
from ... base_types.node import AnimationNode

class ColorMix(bpy.types.Node, AnimationNode):
    bl_idname = "an_ColorMix"
    bl_label = "Color Mix"
    
    def create(self):
        self.inputs.new("an_FloatSocket", "Factor", "factor").setMinMax(0.0, 1.0)
        self.inputs.new("an_ColorSocket", "Color 1", "a")
        self.inputs.new("an_ColorSocket", "Color 2", "b")
        self.outputs.new("an_ColorSocket", "Color", "color")

    def execute(self, factor, a, b):
        newColor = [0, 0, 0, 0]
        factor = min(max(factor, 0), 1)
        for i in range(4):
            newColor[i] = a[i] * (1 - factor) + b[i] * factor
        return newColor
