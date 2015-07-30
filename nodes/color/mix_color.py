import bpy, random
from ... base_types.node import AnimationNode


class ColorMix(bpy.types.Node, AnimationNode):
    bl_idname = "mn_ColorMix"
    bl_label = "Color Mix"
    isDetermined = True
    
    inputNames = { "Factor" : "factor",
                   "Color 1" : "a",
                   "Color 2" : "b" }
                   
    outputNames = { "Color" : "color" }                  
    
    def create(self):
        self.inputs.new("mn_FloatSocket", "Factor")
        self.inputs.new("mn_ColorSocket", "Color 1")
        self.inputs.new("mn_ColorSocket", "Color 2")
        self.outputs.new("mn_ColorSocket", "Color")

    def execute(self, factor, a, b):
        newColor = [0, 0, 0, 0]
        factor = min(max(factor, 0), 1)
        for i in range(4):
            newColor[i] = a[i] * (1 - factor) + b[i] * factor
        return newColor
        

