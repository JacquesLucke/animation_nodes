import bpy
from ... base_types.node import AnimationNode
from ... mn_execution import nodePropertyChanged

class EvaluateInterpolation(bpy.types.Node, AnimationNode):
    bl_idname = "mn_EvaluateInterpolation"
    bl_label = "Evaluate Interpolation"
    isDetermined = True
    
    def create(self):
        self.inputs.new("mn_InterpolationSocket", "Interpolation").showName = False
        self.inputs.new("mn_FloatSocket", "Position").setMinMax(0, 1)
        self.outputs.new("mn_FloatSocket", "Value")
        
    def getInputSocketNames(self):
        return {"Interpolation" : "interpolation",
                "Position" : "position"}
                
    def getOutputSocketNames(self):
        return {"Value" : "value"}
        
    def execute(self, interpolation, position):
        return interpolation[0](max(min(position, 1.0), 0.0), interpolation[1])
