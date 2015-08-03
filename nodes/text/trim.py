import bpy
from ... events import propertyChanged
from ... base_types.node import AnimationNode

class TrimText(bpy.types.Node, AnimationNode):
    bl_idname = "an_TrimText"
    bl_label = "Trim Text"

    inputNames = { "Text" : "text",
                   "Start" : "start",
                   "End" : "end" }

    outputNames = { "Text" : "text" }

    def settingChanged(self, context):
        self.inputs["End"].hide = self.autoEnd
        propertyChanged()

    autoEnd = bpy.props.BoolProperty(default = False, description = "Use the length of the text as trim-end", update = settingChanged)
    allowNegativeIndex = bpy.props.BoolProperty(default = False, description = "Negative indices start from the end", update = settingChanged)

    def create(self):
        self.inputs.new("an_StringSocket", "Text")
        self.inputs.new("an_IntegerSocket", "Start").value = 0
        self.inputs.new("an_IntegerSocket", "End").value = 5
        self.outputs.new("an_StringSocket", "Text")

    def draw_buttons(self, context, layout):
        layout.prop(self, "autoEnd", text = "Auto End")
        layout.prop(self, "allowNegativeIndex", text = "Negative Indices")

    def execute(self, text, start, end):
        textLength = len(text)

        if self.autoEnd: end = textLength

        minIndex = -textLength if self.allowNegativeIndex else 0
        start = min(max(minIndex, start), textLength)
        end = min(max(minIndex, end), textLength)

        return text[start:end]
