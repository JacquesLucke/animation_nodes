import bpy
from bpy.props import *
from ... tree_info import keepNodeLinks
from ... base_types.node import AnimationNode
from ... sockets.info import getBaseDataTypeItems, toListIdName, isBase, toBaseDataType

class SliceListNode(bpy.types.Node, AnimationNode):
    bl_idname = "SliceListNode"
    bl_label = "Slice List"

    def assignedTypeChanged(self, context):
        self.listIdName = toListIdName(self.assignedType)
        self.generateSockets()

    selectedType = EnumProperty(name = "Type", items = getBaseDataTypeItems)
    assignedType = StringProperty(update = assignedTypeChanged)
    listIdName = StringProperty()

    def create(self):
        self.assignedType = "Float"
        self.selectedType = "Float"

    def drawAdvanced(self, layout):
        col = layout.column(align = True)
        col.prop(self, "selectedType", text = "")
        self.invokeFunction(col, "assignSelectedListType",
            text = "Assign",
            description = "Remove all sockets and set the selected socket type")

    def getExecutionCode(self):
        return "slicedList = list[start:end:step]"

    def edit(self):
        baseDataType = self.getWantedDataType()
        self.assignType(baseDataType)

    def getWantedDataType(self):
        listInput = self.inputs["List"].dataOrigin
        listOutputs = self.outputs["List"].dataTargets

        if listInput is not None: return toBaseDataType(listInput.bl_idname)
        if len(listOutputs) == 1: return toBaseDataType(listOutputs[0].bl_idname)
        return toBaseDataType(self.inputs["List"].bl_idname)

    def assignSelectedListType(self):
        self.assignedType = self.selectedType

    def assignType(self, baseDataType):
        if not isBase(baseDataType): return
        if baseDataType == self.assignedType: return
        self.assignedType = baseDataType

    @keepNodeLinks
    def generateSockets(self):
        self.inputs.clear()
        self.outputs.clear()
        self.inputs.new(self.listIdName, "List", "list").dataIsModified  = True
        self.inputs.new("an_IntegerSocket", "Start", "start")
        self.inputs.new("an_IntegerSocket", "End", "end")
        socket = self.inputs.new("an_IntegerSocket", "Step", "step")
        socket.value = 1
        socket.hide = True
        socket.setMinMax(1, 1e7)
        self.outputs.new(self.listIdName, "List", "slicedList")
