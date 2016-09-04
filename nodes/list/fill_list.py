import bpy
from bpy.props import *
from ... tree_info import keepNodeState
from ... events import executionCodeChanged
from ... base_types import AnimationNode
from ... sockets.info import isBase, toBaseDataType, toListDataType

fillModeItems = [
    ("LEFT", "Left", "", "TRIA_LEFT", 0),
    ("RIGHT", "Right", "", "TRIA_RIGHT", 1) ]

class FillListNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_FillListNode"
    bl_label = "Fill List"

    def assignedTypeChanged(self, context):
        self.generateSockets()

    assignedType = StringProperty(update = assignedTypeChanged)

    fillMode = EnumProperty(name = "Fill Mode", default = "RIGHT",
        items = fillModeItems, update = executionCodeChanged)

    makeElementCopies = BoolProperty(name = "Make Element Copies", default = True,
        description = "Insert copies of the original fill element",
        update = executionCodeChanged)

    def create(self):
        self.assignedType = "Float"

    def draw(self, layout):
        layout.prop(self, "fillMode", expand = True)

    def drawAdvanced(self, layout):
        layout.prop(self, "makeElementCopies")
        self.invokeSocketTypeChooser(layout, "assignListDataType",
            socketGroup = "LIST", text = "Change Type", icon = "TRIA_RIGHT")

    def getExecutionCode(self):
        yield "missingAmount = max(length - len(inList), 0)"
        elementSocket = self.inputs["Element"]
        listFromValuesCode = self.outputs[0].getFromValuesCode()
        if self.makeElementCopies and elementSocket.isCopyable():
            yield ("fillList = [{} for _ in range(missingAmount)]"
                    .format(elementSocket.getCopyExpression().replace("value", "fillElement")))
            yield "fillList = " + listFromValuesCode.replace("value", "fillList")
        else:
            yield "fillList = {} * missingAmount".format(listFromValuesCode.replace("value", "[fillElement]"))

        yield "if len(inList) == 0:"
        yield "    outList = fillList"
        yield "else:"
        if self.fillMode == "LEFT":  yield "    outList = fillList + inList"
        if self.fillMode == "RIGHT": yield "    outList = inList + fillList"

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

        baseDataType = self.assignedType
        listDataType = toListDataType(self.assignedType)
        self.newInput("an_IntegerSocket", "Length", "length")
        self.newInput(listDataType, "List", "inList").dataIsModified = True
        self.newInput(baseDataType, "Element", "fillElement")
        self.newOutput(listDataType, "List", "outList")
