import bpy, random
from ... base_types.node import AnimationNode

class FloatClamp(bpy.types.Node, AnimationNode):
    bl_idname = "an_FloatClamp"
    bl_label = "Clamp"

    def create(self):
        self.inputs.new("an_FloatSocket", "Value", "value")
        self.inputs.new("an_FloatSocket", "Min", "minValue").value = 0.0
        self.inputs.new("an_FloatSocket", "Max", "maxValue").value = 1.0
        self.outputs.new("an_FloatSocket", "Value", "outValue")

    def getExecutionCode(self):
        return "outValue = min(max(value, minValue), maxValue)"
