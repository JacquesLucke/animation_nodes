import bpy
from ... base_types.node import AnimationNode

class ReplicateStringsNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ReplicateStringsNode"
    bl_label = "Replicate Text"

    def create(self):
        self.newInput("String", "Text", "text")
        self.newInput("Integer", "Amount", "amount", value = 2, minValue = 0)
        self.newOutput("String", "Text", "outText")

    def getExecutionCode(self):
        return "outText = text * amount"
