import bpy
from ... base_types.node import AnimationNode

class TextBlockWriterNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_TextBlockWriterNode"
    bl_label = "Text Block Writer"

    def create(self):
        self.inputs.new("an_TextBlockSocket", "Text Block", "textBlock").defaultDrawType = "PROPERTY_ONLY"
        self.inputs.new("an_StringSocket", "Text", "text")
        self.inputs.new("an_BooleanSocket", "Enabled", "enabled").hide = True
        self.outputs.new("an_TextBlockSocket", "Text Block", "textBlock")

    def execute(self, textBlock, text, enabled):
        if not enabled or textBlock is None: return textBlock
        textBlock.from_string(text)
        return textBlock
