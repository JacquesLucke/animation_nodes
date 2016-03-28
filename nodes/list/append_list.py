import bpy
from bpy.props import *
from ... tree_info import keepNodeState
from ... base_types.node import AnimationNode
from ... sockets.info import getBaseDataTypeItemsCallback, toIdName, toListIdName, isBase, toBaseDataType, isLimitedList, toGeneralListIdName

class AppendListNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_AppendListNode"
    bl_label = "Append to List"

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
        if self.isTuple(): yield "inList = list(inList)"
        yield "inList.append(element)"

    def edit(self):
        baseDataType = self.getWantedDataType()
        self.assignType(baseDataType)
        
    def isTuple(self):
        listInput = self.inputs["List"].dataOrigin
        if listInput is not None:
            if isLimitedList(listInput.bl_idname): return True
        return False

    def getWantedDataType(self):
        listInput = self.inputs["List"].dataOrigin
        elementInput = self.inputs["Element"].dataOrigin
        listOutputs = self.outputs["List"].dataTargets

        if listInput is not None: 
            idName = listInput.bl_idname
            if isLimitedList(idName): idName = toGeneralListIdName(idName)
            return toBaseDataType(idName)
        if elementInput is not None: return elementInput.dataType
        if len(listOutputs) == 1: return toBaseDataType(listOutputs[0].bl_idname)
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
        self.inputs.new(self.listIdName, "List", "inList").dataIsModified  = True
        self.inputs.new(self.baseIdName, "Element", "element").dataIsModified = True
        self.outputs.new(self.listIdName, "List", "inList")