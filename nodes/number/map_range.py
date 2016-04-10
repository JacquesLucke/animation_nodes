import bpy
from bpy.props import *
from ... tree_info import keepNodeState
from ... base_types.node import AnimationNode

class MapRangeNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MapRangeNode"
    bl_label = "Map Range"
    bl_width_default = 170

    def settingChanged(self, context):
        self.recreateInputs()

    clampInput = BoolProperty(name = "Clamp Input", default = True,
        description = "The input will be between Input Min and Input Max",
        update = settingChanged)

    useInterpolation = BoolProperty(name = "Use Interpolation", default = False,
        description = "Don't use the normal linear interpolation between Min and Max (only available when clamp is turned on)",
        update = settingChanged)

    def create(self):
        self.recreateInputs()
        self.newOutput("an_FloatSocket", "Value", "newValue")

    @keepNodeState
    def recreateInputs(self):
        self.inputs.clear()
        self.newInput("an_FloatSocket", "Value", "value")
        self.newInput("an_FloatSocket", "Input Min", "inMin").value = 0
        self.newInput("an_FloatSocket", "Input Max", "inMax").value = 1
        self.newInput("an_FloatSocket", "Output Min", "outMin").value = 0
        self.newInput("an_FloatSocket", "Output Max", "outMax").value = 1

        if self.useInterpolation and self.clampInput:
            self.newInput("an_InterpolationSocket", "Interpolation", "interpolation").defaultDrawType = "PROPERTY_ONLY"

    def draw(self, layout):
        col = layout.column(align = True)
        col.prop(self, "clampInput")

        subcol = col.column(align = True)
        subcol.active = self.clampInput
        subcol.prop(self, "useInterpolation")

    def getExecutionCode(self):
        yield "if inMin == inMax: newValue = 0"
        yield "else:"
        if self.clampInput:
            yield "    _value = min(max(value, inMin), inMax) if inMin < inMax else min(max(value, inMax), inMin)"
            if self.useInterpolation:
                yield "    newValue = outMin + interpolation((_value - inMin) / (inMax - inMin)) * (outMax - outMin)"
            else:
                yield "    newValue = outMin + (_value - inMin) / (inMax - inMin) * (outMax - outMin)"
        else:
            yield "    newValue = outMin + (value - inMin) / (inMax - inMin) * (outMax - outMin)"
