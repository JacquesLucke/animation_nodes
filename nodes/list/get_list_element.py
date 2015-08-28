import bpy
from bpy.props import *
from ... tree_info import keepNodeLinks
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode
from ... sockets.info import getBaseDataTypeItems, toIdName, toListIdName, isBase, toBaseDataType

class GetListElementNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GetListElementNode"
    bl_label = "Get List Element"

    def assignedTypeChanged(self, context):
        self.baseIdName = toIdName(self.assignedType)
        self.listIdName = toListIdName(self.assignedType)
        self.generateSockets()

    selectedType = EnumProperty(name = "Type", items = getBaseDataTypeItems)
    assignedType = StringProperty(update = assignedTypeChanged)
    baseIdName = StringProperty()
    listIdName = StringProperty()

    allowNegativeIndex = BoolProperty(name = "Allow Negative Index",
        description = "-2 means the second last list element",
        update = executionCodeChanged, default = False)

    def create(self):
        self.assignedType = "Float"
        self.selectedType = "Float"

    def drawAdvanced(self, layout):
        layout.prop(self, "allowNegativeIndex")
        col = layout.column(align = True)
        col.prop(self, "selectedType", text = "")
        self.invokeFunction(col, "assignSelectedListType",
            text = "Assign",
            description = "Remove all sockets and set the selected socket type")

    def getExecutionCode(self):
        if self.allowNegativeIndex: return "element = list[index] if -len(list) <= index < len(list) else fallback"
        return "element = list[index] if 0 <= index < len(list) else fallback"

    def edit(self):
        dataType = self.getWantedDataType()
        self.assignType(dataType)

    def getWantedDataType(self):
        listInput = self.inputs["List"].dataOrigin
        fallbackInput = self.inputs["Fallback"].dataOrigin
        elementOutputs = self.outputs["Element"].dataTargets

        if listInput is not None: return toBaseDataType(listInput.bl_idname)
        if fallbackInput is not None: return fallbackInput.dataType
        if len(elementOutputs) == 1: return elementOutputs[0].dataType
        return self.outputs["Element"].dataType

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
        self.inputs.new(self.listIdName, "List", "list")
        self.inputs.new("an_IntegerSocket", "Index", "index")
        self.inputs.new(self.baseIdName, "Fallback", "fallback")
        self.outputs.new(self.baseIdName, "Element", "element")
