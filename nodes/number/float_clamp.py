import bpy
from ... base_types import AnimationNode, AutoSelectFloatOrInteger

class FloatClampNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_FloatClampNode"
    bl_label = "Clamp"
    dynamicLabelType = "HIDDEN_ONLY"

    def create(self):
        self.newInput("Float", "Value", "value")
        self.newInput("Float", "Min", "minValue", value = 0.0)
        self.newInput("Float", "Max", "maxValue", value = 1.0)
        self.newOutput("Float", "Value", "outValue")

        self.newSocketEffect(AutoSelectFloatOrInteger(self.outputs[0]))

    def getExecutionCode(self):
        yield "outValue = min(max(value, minValue), maxValue)"
        if self.outputs[0].dataType == "Integer":
            yield "outValue = int(outValue)"

    def drawLabel(self):
        label = "clamp(min, max)"
        if self.minValueSocket.isUnlinked:
            label = label.replace("min", str(round(self.minValueSocket.value, 4)))
        if self.maxValueSocket.isUnlinked:
            label = label.replace("max", str(round(self.maxValueSocket.value, 4)))
        return label

    @property
    def minValueSocket(self):
        return self.inputs.get("Min")

    @property
    def maxValueSocket(self):
        return self.inputs.get("Max")
