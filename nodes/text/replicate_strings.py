import bpy
from ... base_types.node import AnimationNode

class ReplicateStringsNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ReplicateStringsNode"
    bl_label = "Replicate Text"

    inputNames = { "Text" : "text",
                   "Amount" : "amount" }

    outputNames = { "Text" : "text" }

    def create(self):
        self.inputs.new("an_StringSocket", "Text")
        socket = self.inputs.new("an_IntegerSocket", "Amount")
        socket.setMinMax(0, 1000000)
        socket.value = 2
        self.outputs.new("an_StringSocket", "Text")

    def getExecutionCode(self):
        return "$text$ = %text% * %amount%"
