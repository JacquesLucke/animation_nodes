import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types.node import AnimationNode

class TrimTextNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_TrimTextNode"
    bl_label = "Trim Text"

    def settingChanged(self, context):
        self.inputs["End"].hide = self.autoEnd
        propertyChanged()

    autoEnd = BoolProperty(
        default = False, update = settingChanged,
        description = "Use the length of the text as trim-end")

    allowNegativeIndex = BoolProperty(
        default = False, update = settingChanged,
        description = "Negative indices start from the end")

    def create(self):
        self.inputs.new("an_StringSocket", "Text", "text")
        self.inputs.new("an_IntegerSocket", "Start", "start").value = 0
        self.inputs.new("an_IntegerSocket", "End", "end").value = 5
        self.outputs.new("an_StringSocket", "Text", "outText")

    def draw(self, layout):
        layout.prop(self, "autoEnd", text = "Auto End")
        layout.prop(self, "allowNegativeIndex", text = "Negative Indices")

    def execute(self, text, start, end):
        textLength = len(text)

        if self.autoEnd: end = textLength

        minIndex = -textLength if self.allowNegativeIndex else 0
        start = min(max(minIndex, start), textLength)
        end = min(max(minIndex, end), textLength)

        return text[start:end]
