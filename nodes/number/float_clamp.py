import bpy
from bpy.props import *
from ... tree_info import keepNodeLinks
from ... base_types.node import AnimationNode

class FloatClampNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_FloatClampNode"
    bl_label = "Clamp"

    def outputIntegerChanged(self, context):
        self.recreateOutputSocket()

    outputInteger = BoolProperty(name = "Output Integer", default = False,
        update = outputIntegerChanged)

    def create(self):
        self.inputs.new("an_FloatSocket", "Value", "value")
        self.inputs.new("an_FloatSocket", "Min", "minValue").value = 0.0
        self.inputs.new("an_FloatSocket", "Max", "maxValue").value = 1.0
        self.outputs.new("an_FloatSocket", "Value", "outValue")

    def getExecutionCode(self):
        yield "outValue = min(max(value, minValue), maxValue)"
        if self.outputInteger: yield "outValue = int(outValue)"

    def drawLabel(self):
        label = "clamp(min, max)"
        if self.minValueSocket.isUnlinked:
            label = label.replace("min", str(round(self.minValueSocket.value, 4)))
        if self.maxValueSocket.isUnlinked:
            label = label.replace("max", str(round(self.maxValueSocket.value, 4)))
        return label

    def edit(self):
        self.outputInteger = self.outputs[0].isOnlyLinkedToDataType("Integer")

    def recreateOutputSocket(self):
        idName = "an_IntegerSocket" if self.outputInteger else "an_FloatSocket"
        if self.outputs[0].bl_idname == idName: return
        self._recreateOutputSocket(idName)

    @keepNodeLinks
    def _recreateOutputSocket(self, idName):
        self.outputs.clear()
        self.outputs.new(idName, "Value", "outValue")

    @property
    def minValueSocket(self):
        return self.inputs.get("Min")

    @property
    def maxValueSocket(self):
        return self.inputs.get("Max")
