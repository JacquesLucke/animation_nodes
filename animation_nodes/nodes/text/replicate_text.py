import bpy
from ... base_types import AnimationNode

class ReplicateTextNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ReplicateTextNode"
    bl_label = "Replicate Text"

    def create(self):
        self.newInput("Text", "Text", "text")
        self.newInput("Integer", "Amount", "amount", value = 2, minValue = 0)
        self.newOutput("Text", "Text", "outText")

    def getExecutionCode(self):
        return "outText = text * amount"
