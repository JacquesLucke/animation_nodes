import bpy
from bpy.props import *
from ... tree_info import keepNodeState
from ... sockets.info import toIdName, isList
from ... base_types.node import AnimationNode

class ShiftListNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ShiftListNode"
    bl_label = "Shift List"

    def assignedTypeChanged(self, context):
        self.listIdName = toIdName(self.assignedType)
        self.generateSockets()

    assignedType = StringProperty(update = assignedTypeChanged)
    listIdName = StringProperty()

    def create(self):
        self.assignedType = "Object List"

    def getExecutionCode(self):
        yield "if len(inList) == 0: shiftedList = []"
        yield "else:"
        yield "    shiftAmount = amount % len(inList)"
        yield "    shiftedList = inList[-shiftAmount:] + inList[:-shiftAmount]"

    def edit(self):
        listDataType = self.getWantedDataType()
        self.assignType(listDataType)

    def getWantedDataType(self):
        listInput = self.inputs[0].dataOrigin
        listOutputs = self.outputs[0].dataTargets

        if listInput is not None: return listInput.dataType
        if len(listOutputs) == 1: return listOutputs[0].dataType
        return self.inputs[0].dataType

    def assignType(self, listDataType):
        if not isList(listDataType): return
        if listDataType == self.assignedType: return
        self.assignedType = listDataType

    @keepNodeState
    def generateSockets(self):
        self.inputs.clear()
        self.outputs.clear()
        self.inputs.new(self.listIdName, "List", "inList").dataIsModified = True
        self.inputs.new("an_IntegerSocket", "Amount", "amount")
        self.outputs.new(self.listIdName, "Shifted List", "shiftedList")
