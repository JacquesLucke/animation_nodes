import bpy
from ... base_types.node import AnimationNode

class FloatRangeListNode(bpy.types.Node, AnimationNode):
    bl_idname = "mn_FloatRangeListNode"
    bl_label = "Number Range"
    isDetermined = True

    inputNames = { "Amount" : "amount",
                   "Start" : "start",
                   "Step" : "step" }

    outputNames = { "List" : "list" }

    def create(self):
        self.inputs.new("mn_IntegerSocket", "Amount").value = 5
        self.inputs.new("mn_FloatSocket", "Start")
        self.inputs.new("mn_FloatSocket", "Step").value = 1
        self.outputs.new("mn_FloatListSocket", "List")

    def execute(self, amount, start, step):
        return [start + i * step for i in range(amount)]
