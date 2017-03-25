import bpy
from bpy.props import *
from ... base_types import AnimationNode
from ... sockets.info import toListDataType
from ... data_structures cimport DoubleList, LongLongList

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

    dataType = StringProperty(default = "Float", update = AnimationNode.refresh)

    floatStepType = EnumProperty(name = "Float Step Type", default = "START_STEP",
        items = floatStepTypeItems, update = AnimationNode.refresh)

    def create(self):
        self.newInput("Integer", "Amount", "amount", value = 5, minValue = 0)

        if self.dataType == "Float":
            self.newInput("Float", "Start", "start")
            if self.floatStepType == "START_STEP":
                self.newInput("Float", "Step", "step", value = 1)
            elif self.floatStepType == "START_STOP":
                self.newInput("Float", "Stop", "stop", value = 4)
        elif self.dataType == "Integer":
            self.newInput("Integer", "Start", "start")
            self.newInput("Integer", "Step", "step", value = 1)

        self.newOutput(toListDataType(self.dataType), "List", "list")

    def draw(self, layout):
        if self.dataType == "Float":
            layout.prop(self, "floatStepType", text = "")

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

    def execute_IntegerRange(self, long amount, long start, long step):
        cdef LongLongList newList = LongLongList(length = max(amount, 0))
        cdef long i
        for i in range(amount):
            newList.data[i] = start + i * step
        return newList

    def execute_FloatRange_StartStep(self, long amount, double start, double step):
        cdef DoubleList newList = DoubleList(length = max(amount, 0))
        cdef long i
        for i in range(amount):
            newList.data[i] = start + i * step
        return newList

    def execute_FloatRange_StartStop(self, long amount, double start, double stop):
        if amount == 0:
            return DoubleList()
        elif amount == 1:
            return DoubleList.fromValues([start])
        elif start == stop:
            return DoubleList.fromValues([start]) * amount
        else:
            return self.execute_FloatRange_StartStep(amount, start, (stop - start) / (amount - 1))
