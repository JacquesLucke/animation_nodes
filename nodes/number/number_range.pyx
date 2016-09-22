import bpy
from bpy.props import *
from ... base_types import AnimationNode
from ... sockets.info import toListDataType
from ... data_structures cimport DoubleList, LongLongList

class NumberRangeNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_NumberRangeNode"
    bl_label = "Number Range"
    dynamicLabelType = "ALWAYS"

    onlySearchTags = True
    searchTags = [ ("Float Range", {"dataType" : repr("Float")}),
                   ("Integer Range", {"dataType" : repr("Integer")}) ]

    dataType = StringProperty(default = "Float", update = AnimationNode.updateSockets)

    def create(self):
        self.newInput("Integer", "Amount", "amount", value = 5)
        self.newInput(self.dataType, "Start", "start")
        self.newInput(self.dataType, "Step", "step", value = 1)
        self.newOutput(toListDataType(self.dataType), "List", "list")

    def drawLabel(self):
        return self.inputs[1].dataType + " Range"

    def getExecutionFunctionName(self):
        if self.dataType == "Integer":
            return "execute_IntegerRange"
        elif self.dataType == "Float":
            return "execute_FloatRange"

    def execute_IntegerRange(self, long amount, long start, long step):
        cdef LongLongList newList = LongLongList(length = max(amount, 0))
        cdef long i
        for i in range(amount):
            newList.data[i] = start + i * step
        return newList

    def execute_FloatRange(self, long amount, double start, double step):
        cdef DoubleList newList = DoubleList(length = max(amount, 0))
        cdef long i
        for i in range(amount):
            newList.data[i] = start + i * step
        return newList
