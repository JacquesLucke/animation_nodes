import bpy
from bpy.props import *
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

class MapRangeNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MapRangeNode"
    bl_label = "Map Range"

    clamp = BoolProperty(name = "Clamp", default = True,
        description = "The output will be between Output Min and Output Max",
        update = executionCodeChanged)

    def create(self):
        self.width = 150
        self.inputs.new("an_FloatSocket", "Value", "value")
        self.inputs.new("an_FloatSocket", "Input Min", "inMin").value = 0
        self.inputs.new("an_FloatSocket", "Input Max", "inMax").value = 1
        self.inputs.new("an_FloatSocket", "Output Min", "outMin").value = 0
        self.inputs.new("an_FloatSocket", "Output Max", "outMax").value = 1
        self.outputs.new("an_FloatSocket", "Value", "newValue")

    def draw(self, layout):
        layout.prop(self, "clamp")

    def getExecutionCode(self):
        unclampedExpression = ("outMin + (value - inMin) / (inMax - inMin) * (outMax - outMin)"
                               " if inMin != inMax else (outMax + outMin) / 2")
        if self.clamp:
            return ("start, end = (outMin, outMax) if outMin < outMax else (outMax, outMin)",
                    "newValue = min(max({}, start), end)".format(unclampedExpression))
        else:
            return "newValue = " + unclampedExpression
