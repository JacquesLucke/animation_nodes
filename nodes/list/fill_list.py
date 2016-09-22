import bpy
from bpy.props import *
from ... events import executionCodeChanged
from ... sockets.info import isBase, toBaseDataType, toListDataType
from ... base_types import AnimationNode, UpdateAssignedListDataType

fillModeItems = [
    ("LEFT", "Left", "", "TRIA_LEFT", 0),
    ("RIGHT", "Right", "", "TRIA_RIGHT", 1) ]

class FillListNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_FillListNode"
    bl_label = "Fill List"

    assignedType = StringProperty(update = AnimationNode.updateSockets, default = "Float")

    fillMode = EnumProperty(name = "Fill Mode", default = "RIGHT",
        items = fillModeItems, update = executionCodeChanged)

    makeElementCopies = BoolProperty(name = "Make Element Copies", default = True,
        description = "Insert copies of the original fill element",
        update = executionCodeChanged)

    def create(self):
        baseDataType = self.assignedType
        listDataType = toListDataType(self.assignedType)

        self.newInput("an_IntegerSocket", "Length", "length")
        self.newInput(listDataType, "List", "inList", dataIsModified = True)
        self.newInput(baseDataType, "Element", "fillElement")
        self.newOutput(listDataType, "List", "outList")

        self.newSocketEffect(UpdateAssignedListDataType("assignedType", "BASE",
            [(self.inputs[1], "LIST"),
             (self.inputs[2], "BASE"),
             (self.outputs[0], "LIST")]
        ))

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

    def assignListDataType(self, listDataType):
        self.assignType(toBaseDataType(listDataType))

    def assignType(self, baseDataType):
        if not isBase(baseDataType): return
        if baseDataType == self.assignedType: return
        self.assignedType = baseDataType
