import bpy
from ... base_types import AnimationNode

class TextLengthNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_TextLengthNode"
    bl_label = "Text Length"

    def create(self):
        self.newInput("Text", "Text", "text")
        self.newOutput("Integer", "Length", "length")

    def getExecutionCode(self):
        return "length = len(text)"
