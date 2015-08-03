import bpy
from ... base_types.node import AnimationNode
from ... algorithms.interpolation import mixedInterpolation

class MixInterpolation(bpy.types.Node, AnimationNode):
    bl_idname = "an_MixInterpolation"
    bl_label = "Mix Interpolation"
    isDetermined = True
    
    inputNames = { "Factor" : "factor",
                   "Interpolation 1" : "a",
                   "Interpolation 2" : "b" }
                   
    outputNames = { "Interpolation" : "interpolation" }
    
    def create(self):
        self.inputs.new("an_FloatSocket", "Factor").setMinMax(0, 1)
        self.inputs.new("an_InterpolationSocket", "Interpolation 1").showName = False
        self.inputs.new("an_InterpolationSocket", "Interpolation 2").showName = False
        self.outputs.new("an_InterpolationSocket", "Interpolation")
        
    def execute(self, factor, a, b):
        return (mixedInterpolation, (a, b, factor))
