import bpy
from ... base_types.node import AnimationNode

class TextBlockWriter(bpy.types.Node, AnimationNode):
    bl_idname = "an_TextBlockWriter"
    bl_label = "Text Block Writer"

    inputNames = { "Text Block" : "textBlock",
                   "Text" : "text",
                   "Enabled" : "enabled" }

    outputNames = { "Text Block" : "textBlock" }

    def create(self):
        self.inputs.new("an_TextBlockSocket", "Text Block").showName = False
        self.inputs.new("an_StringSocket", "Text")
        self.inputs.new("an_BooleanSocket", "Enabled").hide = True
        self.outputs.new("an_TextBlockSocket", "Text Block")

    def execute(self, textBlock, text, enabled):
        if not enabled or textBlock is None: return textBlock
        textBlock.from_string(text)
        return textBlock
