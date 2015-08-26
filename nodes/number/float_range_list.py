import bpy
from ... base_types.node import AnimationNode

class FloatRangeListNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_FloatRangeListNode"
    bl_label = "Number Range"

    def create(self):
        self.inputs.new("an_IntegerSocket", "Amount", "amount").value = 5
        self.inputs.new("an_FloatSocket", "Start", "start")
        self.inputs.new("an_FloatSocket", "Step", "step").value = 1
        self.outputs.new("an_FloatListSocket", "List", "list")

    def getExecutionCode(self):
        return "list = [start + i * step for i in range(amount)]"
