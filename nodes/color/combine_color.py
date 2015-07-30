import bpy, random
from ... base_types.node import AnimationNode


class CombineColor(bpy.types.Node, AnimationNode):
    bl_idname = "mn_CombineColor"
    bl_label = "Combine Color"
    isDetermined = True
    
    inputNames = { "Red" : "red",
                   "Green" : "green",
                   "Blue" : "blue",
                   "Alpha" : "alpha" }
                   
    outputNames = { "Color" : "color" }                 
    
    def create(self):
        self.inputs.new("mn_FloatSocket", "Red")
        self.inputs.new("mn_FloatSocket", "Green")
        self.inputs.new("mn_FloatSocket", "Blue")
        self.inputs.new("mn_FloatSocket", "Alpha").value = 1
        self.outputs.new("mn_ColorSocket", "Color")

    def execute(self, red, green, blue, alpha):
        return [red, green, blue, alpha]