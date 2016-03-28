import bpy
from bpy.props import *
from ... tree_info import keepNodeLinks
from ... base_types.node import AnimationNode
from ... sockets.info import toIdName, isList, isLimitedList, toGeneralListIdName, toDataType

class SliceListNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SliceListNode"
    bl_label = "Slice List"

    def assignedTypeChanged(self, context):
        self.listIdName = toIdName(self.assignedType)
        self.generateSockets()

    assignedType = StringProperty(update = assignedTypeChanged)
    listIdName = StringProperty()

    def create(self):
        self.assignedType = "Float"

    def drawAdvanced(self, layout):
        self.invokeSocketTypeChooser(layout, "assignListDataType",
            socketGroup = "LIST", text = "Change Type", icon = "TRIA_RIGHT")

    def getExecutionCode(self):
        return "slicedList = {}[start:end:step]".format("list(inList)" if self.isTuple() else "inList")

    def edit(self):
        listDataType = self.getWantedDataType()
        self.assignType(listDataType)

    def isTuple(self):
        listInput = self.inputs["List"].dataOrigin
        if listInput is not None:
            if isLimitedList(listInput.bl_idname): return True
        return False

    def getWantedDataType(self):
        listInput = self.inputs[0].dataOrigin
        listOutputs = self.outputs[0].dataTargets

        if listInput is not None: 
            idName = listInput.bl_idname
            if isLimitedList(idName): idName = toGeneralListIdName(idName)
            return toDataType(idName)
        if len(listOutputs) == 1: return listOutputs[0].dataType
        return self.inputs[0].dataType

    def assignListDataType(self, listDataType):
        self.assignType(listDataType)

    def assignType(self, listDataType):
        if not isList(listDataType): return
        if listDataType == self.assignedType: return
        self.assignedType = listDataType

    @keepNodeLinks
    def generateSockets(self):
        self.inputs.clear()
        self.outputs.clear()
        self.inputs.new(self.listIdName, "List", "inList").dataIsModified  = True
        self.inputs.new("an_IntegerSocket", "Start", "start")
        self.inputs.new("an_IntegerSocket", "End", "end")
        socket = self.inputs.new("an_IntegerSocket", "Step", "step")
        socket.value = 1
        socket.hide = True
        socket.minValue = 1
        self.outputs.new(self.listIdName, "List", "slicedList")
