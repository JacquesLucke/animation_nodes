import bpy, random
from ... base_types.node import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling


class mn_ColorMix(bpy.types.Node, AnimationNode):
    bl_idname = "mn_ColorMix"
    bl_label = "Color Mix"
    isDetermined = True
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_FloatSocket", "Factor")
        self.inputs.new("mn_ColorSocket", "Color 1")
        self.inputs.new("mn_ColorSocket", "Color 2")
        self.outputs.new("mn_ColorSocket", "Color")
        allowCompiling()

    def getInputSocketNames(self):
        return {"Factor" : "factor",
                "Color 1" : "a",
                "Color 2" : "b"}
    def getOutputSocketNames(self):
        return {"Color" : "color"}

    def execute(self, factor, a, b):
        newColor = [0, 0, 0, 0]
        factor = min(max(factor, 0), 1)
        for i in range(4):
            newColor[i] = a[i] * (1 - factor) + b[i] * factor
        return newColor
        

