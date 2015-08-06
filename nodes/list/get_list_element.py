import bpy
from bpy.props import *
from ... tree_info import keepNodeLinks
from ... base_types.node import AnimationNode
from ... sockets.info import getBaseDataTypeItems, toIdName, toListIdName, isBase, toBaseDataType

class GetListElementNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GetListElementNode"
    bl_label = "Get List Element"

    inputNames = { "List" : "list",
                   "Index" : "index",
                   "Fallback" : "fallback" }

    outputNames = { "Element" : "element" }

    def assignedTypeChanged(self, context):
        self.baseIdName = toIdName(self.assignedType)
        self.listIdName = toListIdName(self.assignedType)
        self.generateSockets()

    selectedType = EnumProperty(name = "Type", items = getBaseDataTypeItems)
    assignedType = StringProperty(update = assignedTypeChanged)
    baseIdName = StringProperty()
    listIdName = StringProperty()

    def create(self):
        self.assignedType = "Float"
        self.selectedType = "Float"

    def draw_buttons_ext(self, context, layout):
        col = layout.column(align = True)
        col.prop(self, "selectedType", text = "")
        self.callFunctionFromUI(col, "assignSelectedListType",
            text = "Assign",
            description = "Remove all sockets and set the selected socket type")

    def execute(self, list, index, fallback):
        if 0 <= index < len(list):
            return list[index]
        return fallback

    def edit(self):
        dataType = self.getWantedDataType()
        self.assignType(dataType)

    def getWantedDataType(self):
        listInput = self.inputs["List"].dataOriginSocket
        fallbackInput = self.inputs["Fallback"].dataOriginSocket
        elementOutputs = self.outputs["Element"].dataTargetSockets

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
        self.inputs.new(self.listIdName, "List")
        self.inputs.new("an_IntegerSocket", "Index")
        self.inputs.new(self.baseIdName, "Fallback")
        self.outputs.new(self.baseIdName, "Element")
