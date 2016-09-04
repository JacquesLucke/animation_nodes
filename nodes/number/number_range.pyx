import bpy
from bpy.props import *
from ... sockets.info import toListDataType
from ... utils.handlers import validCallback
from ... base_types import AnimationNode
from ... data_structures cimport DoubleList, LongLongList

class NumberRangeNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_NumberRangeNode"
    bl_label = "Number Range"
    dynamicLabelType = "ALWAYS"

    onlySearchTags = True
    searchTags = [ ("Float Range", {"dataType" : repr("Float")}),
                   ("Integer Range", {"dataType" : repr("Integer")}) ]

    @validCallback
    def dataTypeChanged(self, context):
        self.generateSockets()

    dataType = StringProperty(default = "Float", update = dataTypeChanged)

    def create(self):
        self.generateSockets()

    def drawLabel(self):
        return self.inputs[1].dataType + " Range"

    def generateSockets(self):
        self.inputs.clear()
        self.outputs.clear()

        self.newInput("Integer", "Amount", "amount", value = 5)
        self.newInput(self.dataType, "Start", "start")
        self.newInput(self.dataType, "Step", "step", value = 1)
        self.newOutput(toListDataType(self.dataType), "List", "list")

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
