import bpy
from bpy.props import *
from ... tree_info import keepNodeState
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode
from ... sockets.info import toIdName, toListIdName, isBase, toBaseDataType

fillModeItems = [
    ("LEFT", "Left", "", "TRIA_LEFT", 0),
    ("RIGHT", "Right", "", "TRIA_RIGHT", 1) ]

class FillListNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_FillListNode"
    bl_label = "Fill List"

    def assignedTypeChanged(self, context):
        self.baseIdName = toIdName(self.assignedType)
        self.listIdName = toListIdName(self.assignedType)
        self.generateSockets()

    assignedType = StringProperty(update = assignedTypeChanged)
    baseIdName = StringProperty()
    listIdName = StringProperty()

    fillMode = EnumProperty(name = "Fill Mode", default = "RIGHT",
        items = fillModeItems, update = executionCodeChanged)

    def create(self):
        self.assignedType = "Float"

    def draw(self, layout):
        layout.prop(self, "fillMode", expand = True)

    def drawAdvanced(self, layout):
        self.invokeSocketTypeChooser(layout, "assignListDataType",
            socketGroup = "LIST", text = "Change Type", icon = "TRIA_RIGHT")

    def getExecutionCode(self):
        yield ("fillList = [{} for i in range(max(length - len(inList), 0))]"
                .format(self.getCopyString(self.inputs["Element"], "fillElement")))

        if self.fillMode == "LEFT": yield "outList = fillList + inList"
        if self.fillMode == "RIGHT": yield "outList = inList + fillList"

    def getCopyString(self, fromSocket, variableString):
        if not fromSocket.isCopyable(): return variableString
        return fromSocket.getCopyExpression().replace("value", variableString)

    def edit(self):
        baseDataType = self.getWantedDataType()
        self.assignType(baseDataType)

    def getWantedDataType(self):
        listInput = self.inputs["List"].dataOrigin
        elementInput = self.inputs["Element"].dataOrigin
        listOutputs = self.outputs["List"].dataTargets

        if listInput is not None: return toBaseDataType(listInput.bl_idname)
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

        self.inputs.new("an_IntegerSocket", "Length", "length")
        self.inputs.new(self.listIdName, "List", "inList").dataIsModified = True
        self.inputs.new(self.baseIdName, "Element", "fillElement")
        self.outputs.new(self.listIdName, "List", "outList")
