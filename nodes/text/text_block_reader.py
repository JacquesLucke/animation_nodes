import bpy
from ... base_types.node import AnimationNode

class TextBlockReaderNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_TextBlockReaderNode"
    bl_label = "Text Block Reader"

    def create(self):
        self.newInput("an_TextBlockSocket", "Text Block", "textBlock").defaultDrawType = "PROPERTY_ONLY"
        self.newOutput("an_StringSocket", "Text", "text")

    def execute(self, textBlock):
        if textBlock is None: return ""
        else: return textBlock.as_string()
