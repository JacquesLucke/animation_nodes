import bpy
from bpy.props import *
from ... tree_info import keepNodeState
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode
from ... sockets.info import isBase, toBaseDataType, toListDataType

class GetListElementNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GetListElementNode"
    bl_label = "Get List Element"
    dynamicLabelType = "HIDDEN_ONLY"

    def assignedTypeChanged(self, context):
        self.generateSockets()

    assignedType = StringProperty(update = assignedTypeChanged)

    clampIndex = BoolProperty(name = "Clamp Index", default = False,
        description = "Clamp the index between the lowest and highest possible index",
        update = executionCodeChanged)

    allowNegativeIndex = BoolProperty(name = "Allow Negative Index",
        description = "-2 means the second last list element",
        update = executionCodeChanged, default = False)

    makeCopy = BoolProperty(name = "Make Copy", default = True,
        description = "Output a copy of the list element to make it independed",
        update = executionCodeChanged)

    def create(self):
        self.assignedType = "Float"

    def drawAdvanced(self, layout):
        layout.prop(self, "clampIndex")
        layout.prop(self, "allowNegativeIndex")
        layout.prop(self, "makeCopy")
        self.invokeSocketTypeChooser(layout, "assignListDataType",
            socketGroup = "LIST", text = "Change Type", icon = "TRIA_RIGHT")

    def drawLabel(self):
        if self.inputs["Index"].isUnlinked:
            return "List[{}]".format(self.inputs["Index"].value)
        return "Get List Element"

    def getExecutionCode(self):
        if self.allowNegativeIndex:
            if self.clampIndex:
                yield "if len(list) != 0: element = list[min(max(index, -len(list)), len(list) - 1)]"
                yield "else: element = fallback"
            else:
                yield "element = list[index] if -len(list) <= index < len(list) else fallback"
        else:
            if self.clampIndex:
                yield "if len(list) != 0: element = list[min(max(index, 0), len(list) - 1)]"
                yield "else: element = fallback"
            else:
                yield "element = list[index] if 0 <= index < len(list) else fallback"

        if self.makeCopy:
            socket = self.outputs[0]
            if socket.isCopyable():
                yield "element = " + socket.getCopyExpression().replace("value", "element")

    def edit(self):
        dataType = self.getWantedDataType()
        self.assignType(dataType)

    def getWantedDataType(self):
        listInput = self.inputs["List"].dataOrigin
        fallbackInput = self.inputs["Fallback"].dataOrigin
        elementOutputs = self.outputs["Element"].dataTargets

        if listInput is not None:
            if listInput.dataType in ("Edge Indices", "Polygon Indices"): return "Integer"
            return toBaseDataType(listInput.dataType)
        if fallbackInput is not None: return fallbackInput.dataType
        if len(elementOutputs) == 1: return elementOutputs[0].dataType
        return self.outputs["Element"].dataType

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

        baseDataType = self.assignedType
        listDataType = toListDataType(self.assignedType)
        self.newInput(listDataType, "List", "list")
        self.newInput("Integer", "Index", "index")
        self.newInput(baseDataType, "Fallback", "fallback").hide = True
        self.newOutput(baseDataType, "Element", "element")
