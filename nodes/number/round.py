import bpy
from ... base_types.node import AnimationNode

class RoundNumberNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_RoundNumberNode"
    bl_label = "Round Number"

    def create(self):
        self.newInput("an_FloatSocket", "Number", "number")
        self.newInput("an_IntegerSocket", "Decimals", "decimals")
        self.newOutput("an_FloatSocket", "Result", "result")

    def getExecutionCode(self):
        yield "result  = int(round(number, decimals)) if decimals <= 0 else round(number, decimals)"
