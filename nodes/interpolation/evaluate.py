import bpy
from ... base_types.node import AnimationNode

class EvaluateInterpolationNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_EvaluateInterpolationNode"
    bl_label = "Evaluate Interpolation"
    bl_width_default = 150

    def create(self):
        self.newInput("Float", "Position", "position").setRange(0, 1)
        self.newInput("Interpolation", "Interpolation", "interpolation", defaultDrawType = "PROPERTY_ONLY")
        self.newOutput("Float", "Value", "value")

    def getExecutionCode(self):
        return "value = interpolation(max(min(position, 1.0), 0.0))"
