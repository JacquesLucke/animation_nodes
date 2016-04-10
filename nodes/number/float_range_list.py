import bpy
from bpy.props import *
from ... sockets.info import toIdName, toListIdName
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

class FloatRangeListNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_FloatRangeListNode"
    bl_label = "Number Range"
    dynamicLabelType = "ALWAYS"

    onlySearchTags = True
    searchTags = [ ("Float Range", {"dataType" : repr("Float")}),
                   ("Integer Range", {"dataType" : repr("Integer")}) ]

    def dataTypeChanged(self, context):
        self.generateSockets()
        executionCodeChanged()

    dataType = StringProperty(default = "Float", update = dataTypeChanged)

    def create(self):
        self.generateSockets()

    def drawLabel(self):
        return self.inputs[1].dataType + " Range"

    def generateSockets(self):
        self.inputs.clear()
        self.outputs.clear()

        baseIdName = toIdName(self.dataType)
        listIdName = toListIdName(self.dataType)
        self.newInput("an_IntegerSocket", "Amount", "amount").value = 5
        self.newInput(baseIdName, "Start", "start")
        self.newInput(baseIdName, "Step", "step").value = 1
        self.newOutput(listIdName, "List", "list")

    def getExecutionCode(self):
        if self.dataType == "Float":
            return "list = [start + i * step for i in range(amount)]"
        if self.dataType == "Integer":
            return "list = [int(start + i * step) for i in range(amount)]"
