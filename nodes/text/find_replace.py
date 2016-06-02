import bpy
from ... base_types.node import AnimationNode

class ReplaceTextNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ReplaceTextNode"
    bl_label = "Replace Text"

    def create(self):
        self.newInput("String", "Text", "text")
        self.newInput("String", "Old", "old")
        self.newInput("String", "New", "new")
        self.newOutput("String", "Text", "newText")

    def getExecutionCode(self):
        return "newText = text.replace(old, new)"
