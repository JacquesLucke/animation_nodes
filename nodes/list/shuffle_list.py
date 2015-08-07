import bpy
from bpy.props import *
from ... tree_info import keepNodeLinks
from ... sockets.info import toIdName, isList
from ... base_types.node import AnimationNode

class ShuffleListNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ShuffleListNode"
    bl_label = "Shuffle List"

    inputNames = { "List" : "list" }
    outputNames = { "Shuffled List" : "shuffledList" }

    def assignedTypeChanged(self, context):
        self.listIdName = toIdName(self.assignedType)
        self.generateSockets()

    assignedType = StringProperty(update = assignedTypeChanged)
    listIdName = StringProperty()

    def create(self):
        self.assignedType = "Object List"

    def getExecutionCode(self, outputUse):
        return ("random.seed(%seed%) \n"
                "$shuffledList$ = %list%[:] \n"
                "random.shuffle($shuffledList$)")

    def edit(self):
        listDataType = self.getWantedDataType()
        self.assignType(listDataType)

    def getWantedDataType(self):
        listInput = self.inputs[0].dataOriginSocket
        listOutputs = self.outputs[0].dataTargetSockets

        if listInput is not None: return listInput.dataType
        if len(listOutputs) == 1: return listOutputs[0].dataType
        return self.inputs[0].dataType

    def assignType(self, listDataType):
        if not isList(listDataType): return
        if listDataType == self.assignedType: return
        self.assignedType = listDataType

    @keepNodeLinks
    def generateSockets(self):
        self.inputs.clear()
        self.outputs.clear()
        self.inputs.new(self.listIdName, "List")
        self.inputs.new("an_IntegerSocket", "Seed")
        self.outputs.new(self.listIdName, "Shuffled List")
