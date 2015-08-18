import bpy
from ... base_types.node import AnimationNode

class TextBlockReader(bpy.types.Node, AnimationNode):
    bl_idname = "an_TextBlockReader"
    bl_label = "Text Block Reader"

    def create(self):
        self.inputs.new("an_TextBlockSocket", "Text Block", "textBlock").showName = False
        self.outputs.new("an_StringSocket", "Text", "text")

    def execute(self, textBlock):
        if textBlock is None: return ""
        else: return textBlock.as_string()
