import bpy
from ... base_types.node import AnimationNode

class ReplaceTextNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ReplaceTextNode"
    bl_label = "Replace Text"

    def create(self):
        self.inputs.new("an_StringSocket", "Text", "text")
        self.inputs.new("an_StringSocket", "Old", "old")
        self.inputs.new("an_StringSocket", "New", "new")
        self.outputs.new("an_StringSocket", "Text", "newText")

    def getExecutionCode(self):
        return "newText = text.replace(old, new)"
