import bpy
from ... base_types.node import AnimationNode

class ReplicateStringsNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ReplicateStringsNode"
    bl_label = "Replicate Text"

    def create(self):
        self.inputs.new("an_StringSocket", "Text", "text")
        socket = self.inputs.new("an_IntegerSocket", "Amount", "amount")
        socket.minValue = 0
        socket.value = 2
        self.outputs.new("an_StringSocket", "Text", "outText")

    def getExecutionCode(self):
        return "outText = text * amount"
