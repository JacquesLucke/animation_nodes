import bpy, random
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling


class mn_CombineColor(bpy.types.Node, AnimationNode):
    bl_idname = "mn_CombineColor"
    bl_label = "Combine Color"
    isDetermined = True
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_FloatSocket", "Red")
        self.inputs.new("mn_FloatSocket", "Green")
        self.inputs.new("mn_FloatSocket", "Blue")
        self.inputs.new("mn_FloatSocket", "Alpha").number = 1
        self.outputs.new("mn_ColorSocket", "Color")
        allowCompiling()

    def getInputSocketNames(self):
        return {"Red" : "red",
                "Green" : "green",
                "Blue" : "blue",
                "Alpha" : "alpha"}
    def getOutputSocketNames(self):
        return {"Color" : "color"}

    def execute(self, red, green, blue, alpha):
        return [red, green, blue, alpha]
        

