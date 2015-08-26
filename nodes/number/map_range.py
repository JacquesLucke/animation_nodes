import bpy
from ... base_types.node import AnimationNode

class MapRangeNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MapRangeNode"
    bl_label = "Map Range"

    def create(self):
        self.inputs.new("an_FloatSocket", "Value", "value")
        self.inputs.new("an_FloatSocket", "Input Min", "inMin").value = 0
        self.inputs.new("an_FloatSocket", "Input Max", "inMax").value = 1
        self.inputs.new("an_FloatSocket", "Output Min", "outMin").value = 0
        self.inputs.new("an_FloatSocket", "Output Max", "outMax").value = 1
        self.outputs.new("an_FloatSocket", "Value", "newValue")

    def getExecutionCode(self):
        return "newValue = outMin + (value - inMin) / (inMax - inMin) * (outMax - outMin)"
