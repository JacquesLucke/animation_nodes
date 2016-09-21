import bpy
from bpy.props import *
from ... tree_info import keepNodeLinks
from ... base_types import AnimationNode

class FloatClampNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_FloatClampNode"
    bl_label = "Clamp"
    dynamicLabelType = "HIDDEN_ONLY"

    def create(self):
        self.newInput("Float", "Value", "value")
        self.newInput("Float", "Min", "minValue", value = 0.0)
        self.newInput("Float", "Max", "maxValue", value = 1.0)
        self.newOutput("Float", "Value", "outValue")

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

    def edit(self):
        output = self.outputs[0]
        if output.dataType == "Float":
            if output.shouldBeIntegerSocket(): self.setOutputType("Integer")
        else:
            if output.shouldBeFloatSocket(): self.setOutputType("Float")

    def setOutputType(self, idName):
        if self.outputs[0].bl_idname == idName: return
        self._setOutputType(idName)

    @keepNodeLinks
    def _setOutputType(self, idName):
        self.outputs.clear()
        self.newOutput(idName, "Value", "outValue")

    @property
    def minValueSocket(self):
        return self.inputs.get("Min")

    @property
    def maxValueSocket(self):
        return self.inputs.get("Max")
