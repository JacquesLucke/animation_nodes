import bpy
from ... base_types.node import AnimationNode

class TextBlockReader(bpy.types.Node, AnimationNode):
    bl_idname = "mn_TextBlockReader"
    bl_label = "Text Block Reader"

    inputNames = { "Text Block" : "textBlock" }
    outputNames = { "Text" : "text" }

    def create(self):
        self.inputs.new("mn_TextBlockSocket", "Text Block").showName = False
        self.outputs.new("mn_StringSocket", "Text")

    def execute(self, textBlock):
        if textBlock is None: return ""
        else: return textBlock.as_string()
