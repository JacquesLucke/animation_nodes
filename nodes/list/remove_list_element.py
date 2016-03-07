import bpy
from bpy.props import *
from ... tree_info import keepNodeState
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode
from ... sockets.info import toIdName, toListIdName, toBaseDataType, isBase, isLimitedList, toGeneralListIdName

class RemoveListElementNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_RemoveListElementNode"
    bl_label = "Remove List Element"

    def assignedTypeChanged(self, context):
        self.baseIdName = toIdName(self.assignedType)
        self.listIdName = toListIdName(self.assignedType)
        self.generateSockets()

    assignedType = StringProperty(update = assignedTypeChanged)
    baseIdName = StringProperty()
    listIdName = StringProperty()

    def create(self):
        self.assignedType = "Float"

    def drawAdvanced(self, layout):
        self.invokeSocketTypeChooser(layout, "assignListDataType",
            socketGroup = "LIST", text = "Change Type", icon = "TRIA_RIGHT")

    def getExecutionCode(self):
        yield "try: list.remove(element)"
        yield "except: pass"

    def edit(self):
        dataType = self.getWantedDataType()
        self.assignType(dataType)

    def getWantedDataType(self):
        listInput = self.inputs["List"].dataOrigin
        elementInput = self.inputs["Element"].dataOrigin
        listOutputs = self.outputs["List"].dataTargets

        if listInput is not None:
            idName = listInput.bl_idname
            if isLimitedList(idName): idName = toGeneralListIdName(idName)
            return toBaseDataType(idName)
        if elementInput is not None: return elementInput.dataType
        if len(listOutputs) == 1: return toBaseDataType(listOutputs[0].dataType)
        return self.inputs["Element"].dataType

    def assignListDataType(self, listDataType):
        self.assignType(toBaseDataType(listDataType))

    def assignType(self, baseDataType):
        if not isBase(baseDataType): return
        if baseDataType == self.assignedType: return
        self.assignedType = baseDataType

    @keepNodeState
    def generateSockets(self):
        self.inputs.clear()
        self.outputs.clear()
        self.inputs.new(self.listIdName, "List", "list").dataIsModified = True
        self.inputs.new(self.baseIdName, "Element", "element").defaultDrawType = "PREFER_PROPERTY"
        self.outputs.new(self.listIdName, "List", "list")
