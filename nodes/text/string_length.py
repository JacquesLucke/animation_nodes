import bpy
from ... base_types.node import AnimationNode

class StringLengthNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_StringLengthNode"
    bl_label = "Text Length"

    def create(self):
        self.newInput("String", "Text", "text")
        self.newOutput("Integer", "Length", "length")

    def getExecutionCode(self):
        return "length = len(text)"
