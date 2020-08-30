import bpy
from bpy.props import *
from ... base_types import AnimationNode
from ... data_structures import DoubleList
from ... events import executionCodeChanged
from ... sockets.info import toListDataType
from ... algorithms.interpolations import Linear as LinearInterpolation

from . c_utils import (
    range_LongList_StartStep,
    range_DoubleList_StartStep,
    range_DoubleList_StartStep_Interpolated,
)

floatStepTypeItems = [
    ("START_STEP", "Start / Step", "", "NONE", 0),
    ("START_STOP", "Start / Stop", "", "NONE", 1)
]

class NumberRangeNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_NumberRangeNode"
    bl_label = "Number Range"
    dynamicLabelType = "ALWAYS"

    onlySearchTags = True
    searchTags = [ ("Float Range", {"dataType" : repr("Float")}),
                   ("Integer Range", {"dataType" : repr("Integer")}) ]

    dataType: StringProperty(default = "Float", update = AnimationNode.refresh)

    floatStepType: EnumProperty(name = "Float Step Type", default = "START_STEP",
        items = floatStepTypeItems, update = AnimationNode.refresh)

    includeEndPoint: BoolProperty(name = "Include End Point", default = True,
        update = executionCodeChanged)

    def create(self):
        self.newInput("Integer", "Amount", "amount", value = 5, minValue = 0)

        if self.dataType == "Float":
            self.newInput("Float", "Start", "start")
            if self.floatStepType == "START_STEP":
                self.newInput("Float", "Step", "step", value = 1)
            elif self.floatStepType == "START_STOP":
                self.newInput("Float", "Stop", "stop", value = 1)
            self.newInput("Interpolation", "Interpolation", "interpolation",
                defaultDrawType = "PROPERTY_ONLY", hide = True)
        elif self.dataType == "Integer":
            self.newInput("Integer", "Start", "start")
            self.newInput("Integer", "Step", "step", value = 1)

        self.newOutput(toListDataType(self.dataType), "List", "list")

    def draw(self, layout):
        if self.dataType == "Float":
            layout.prop(self, "floatStepType", text = "")
            if self.floatStepType == "START_STOP":
                layout.prop(self, "includeEndPoint")

    def drawLabel(self):
        return self.inputs[1].dataType + " Range"

    def getExecutionFunctionName(self):
        if self.dataType == "Integer":
            return "execute_IntegerRange"
        elif self.dataType == "Float":
            if self.floatStepType == "START_STEP":
                return "execute_FloatRange_StartStep"
            elif self.floatStepType == "START_STOP":
                return "execute_FloatRange_StartStop"

    def execute_IntegerRange(self, amount, start, step):
        return range_LongList_StartStep(amount, start, step)

    def execute_FloatRange_StartStep(self, amount, start, step, interpolation):
        if amount <= 0: return DoubleList()
        if amount == 1: return DoubleList.fromValues([start])

        if isinstance(interpolation, LinearInterpolation):
            return range_DoubleList_StartStep(amount, start, step)
        else:
            return range_DoubleList_StartStep_Interpolated(amount, start,
                step, interpolation)

    def execute_FloatRange_StartStop(self, amount, start, stop, interpolation):
        if amount <= 0: return DoubleList()
        if amount == 1: return DoubleList.fromValues([start])

        if self.includeEndPoint:
            step = (stop - start) / (amount - 1)
        else:
            step = (stop - start) / amount

        if isinstance(interpolation, LinearInterpolation):
            return range_DoubleList_StartStep(amount, start, step)
        else:
            return range_DoubleList_StartStep_Interpolated(amount, start,
                step, interpolation)
