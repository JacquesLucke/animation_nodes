import bpy
from ... base_types.node import AnimationNode

class RoundNumberNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_RoundNumberNode"
    bl_label = "Round Number"

    def create(self):
        self.inputs.new("an_FloatSocket", "Number", "number")
        self.inputs.new("an_IntegerSocket", "Decimals", "decimals")
        self.outputs.new("an_FloatSocket", "Result", "result")

    def getExecutionCode(self):
        yield "result  = int(round(number, decimals)) if decimals <= 0 else round(number, decimals)"
