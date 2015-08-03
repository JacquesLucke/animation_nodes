import bpy, random
from ... base_types.node import AnimationNode


class CombineColor(bpy.types.Node, AnimationNode):
    bl_idname = "an_CombineColor"
    bl_label = "Combine Color"
    isDetermined = True
    
    inputNames = { "Red" : "red",
                   "Green" : "green",
                   "Blue" : "blue",
                   "Alpha" : "alpha" }
                   
    outputNames = { "Color" : "color" }                 
    
    def create(self):
        self.inputs.new("an_FloatSocket", "Red")
        self.inputs.new("an_FloatSocket", "Green")
        self.inputs.new("an_FloatSocket", "Blue")
        self.inputs.new("an_FloatSocket", "Alpha").value = 1
        self.outputs.new("an_ColorSocket", "Color")

    def execute(self, red, green, blue, alpha):
        return [red, green, blue, alpha]