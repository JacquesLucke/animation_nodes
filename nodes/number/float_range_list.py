import bpy
from ... base_types.node import AnimationNode

class FloatRangeListNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_FloatRangeListNode"
    bl_label = "Number Range"
    isDetermined = True

    inputNames = { "Amount" : "amount",
                   "Start" : "start",
                   "Step" : "step" }

    outputNames = { "List" : "list" }

    def create(self):
        self.inputs.new("an_IntegerSocket", "Amount").value = 5
        self.inputs.new("an_FloatSocket", "Start")
        self.inputs.new("an_FloatSocket", "Step").value = 1
        self.outputs.new("an_FloatListSocket", "List")

    def execute(self, amount, start, step):
        return [start + i * step for i in range(amount)]
