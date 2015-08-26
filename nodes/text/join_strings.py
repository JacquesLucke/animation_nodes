import bpy
from ... base_types.node import AnimationNode

class JoinStringsNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_JoinStringsNode"
    bl_label = "Join Texts"

    def create(self):
        self.inputs.new("an_StringListSocket", "Texts", "texts")
        self.inputs.new("an_StringSocket", "Separator", "separator")
        self.outputs.new("an_StringSocket", "Text", "text")

    def getExecutionCode(self):
        return "text = separator.join(texts)"
