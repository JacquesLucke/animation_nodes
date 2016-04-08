import bpy
from ... base_types.node import AnimationNode

class RoundNumberNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_RoundNumberNode"
    bl_label = "Round Number"
    dynamicLabelType = "HIDDEN_ONLY"

    def create(self):
        self.inputs.new("an_FloatSocket", "Number", "number")
        self.inputs.new("an_IntegerSocket", "Decimals", "decimals")
        self.outputs.new("an_FloatSocket", "Result", "result")

    def drawLabel(self):
        label = "Round Nr, Decimals"
        if getattr(self.socketNumber, "isUnlinked", False):
            label = label.replace("Nr", str(round(self.socketNumber.value, 4)))
        if getattr(self.socketDecimals, "isUnlinked", False):
            label = label.replace("Decimals", str(self.socketDecimals.value))
        return label

    def getExecutionCode(self):
        yield "result  = int(round(number, decimals)) if decimals <= 0 else round(number, decimals)"

    @property
    def socketNumber(self):
        return self.inputs.get("Number")

    @property
    def socketDecimals(self):
        return self.inputs.get("Decimals")