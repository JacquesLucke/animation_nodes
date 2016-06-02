import bpy
from ... base_types.node import AnimationNode

class JoinStringsNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_JoinStringsNode"
    bl_label = "Join Texts"

    def create(self):
        self.newInput("String List", "Texts", "texts")
        self.newInput("String", "Separator", "separator")
        self.newOutput("String", "Text", "text")

    def getExecutionCode(self):
        return "text = separator.join(texts)"
