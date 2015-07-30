import bpy
from ... base_types.node import AnimationNode

class EvaluateInterpolation(bpy.types.Node, AnimationNode):
    bl_idname = "mn_EvaluateInterpolation"
    bl_label = "Evaluate Interpolation"
    isDetermined = True
    
    inputNames = { "Interpolation" : "interpolation",
                   "Position" : "position" }
                   
    outputNames = { "Value" : "value" }                   
    
    def create(self):
        self.inputs.new("mn_InterpolationSocket", "Interpolation").showName = False
        self.inputs.new("mn_FloatSocket", "Position").setMinMax(0, 1)
        self.outputs.new("mn_FloatSocket", "Value")
        
    def execute(self, interpolation, position):
        return interpolation[0](max(min(position, 1.0), 0.0), interpolation[1])