import bpy
from ... base_types.node import AnimationNode

class EvaluateInterpolation(bpy.types.Node, AnimationNode):
    bl_idname = "an_EvaluateInterpolation"
    bl_label = "Evaluate Interpolation"

    def create(self):
        self.inputs.new("an_InterpolationSocket", "Interpolation", "interpolation").showName = False
        self.inputs.new("an_FloatSocket", "Position", "position").setMinMax(0, 1)
        self.outputs.new("an_FloatSocket", "Value", "value")

    def getExecutionCode(self):
        return "value = interpolation[0](max(min(position, 1.0), 0.0), interpolation[1])"
