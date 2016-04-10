import bpy
import random
from bpy.props import *
from ... tree_info import keepNodeState
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode
from ... sockets.info import toIdName, isList, toBaseDataType, isCopyable, getCopyExpression

repetitionTypeItems = [
    ("LOOP", "Loop", "Repeat", "NONE", 0),
    ("PING_PONG", "Ping Pong", "Repeat and Reverse", "NONE", 1)]

amountTypeItems = [
    ("AMOUNT", "Amount", "Repeat N Times", "NONE", 0),
    ("LENGTH", "Length", "Repeat up to length and cut off the rest", "NONE", 1),
    ("LENGTH_FLOOR", "Below Length", "Repeat up to Length, needs fill till length", "NONE", 2),
    ("LENGTH_CEIL", "Above Length", "Repeat over Length, needs slice down to length", "NONE", 3)]

class RepeatListNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_RepeatListNode"
    bl_label = "Repeat  List"

    def assignedTypeChanged(self, context):
        self.listIdName = toIdName(self.assignedType)
        self.generateSockets()

    assignedType = StringProperty(update = assignedTypeChanged)
    listIdName = StringProperty()

    def repetitionTypeChanged(self, context):
        self.generateSockets()

    def amountTypeChanged(self, context):
        self.generateSockets()

    repetitionType = EnumProperty(name = "Repeat Type", default = "LOOP",
        items = repetitionTypeItems, update = repetitionTypeChanged)

    amountType = EnumProperty(name = "Amount Type", default = "AMOUNT",
        items = amountTypeItems, update = amountTypeChanged)

    makeElementCopies = BoolProperty(name = "Make Element Copies", default = True,
        description = "Insert copies of the original elements",
        update = executionCodeChanged)

    def create(self):
        self.assignedType = "Float List"
        self.generateSockets()

    @keepNodeState
    def generateSockets(self):
        self.inputs.clear()
        self.outputs.clear()

        self.inputs.new(self.listIdName, "List", "inList")
        if self.amountType == "AMOUNT":
            self.inputs.new("an_IntegerSocket", "Amount", "amount").value = 5
        elif "LENGTH" in self.amountType:
            self.inputs.new("an_IntegerSocket", "Length", "length").value = 20
        self.outputs.new(self.listIdName, "List", "outList")

    def draw(self, layout):
        col = layout.column()
        col.prop(self, "repetitionType", text = "")
        col.prop(self, "amountType", text = "")

    def drawAdvanced(self, layout):
        layout.prop(self, "makeElementCopies")
        self.invokeSocketTypeChooser(layout, "assignListDataType",
            socketGroup = "LIST", text = "Change Type", icon = "TRIA_RIGHT")

    def getExecutionCode(self):
        elementDataType = toBaseDataType(self.assignedType)
        makeCopies = isCopyable(elementDataType) and self.makeElementCopies
        if makeCopies:
            copyExpression = getCopyExpression(elementDataType)

        yield "inLength = len(inList)"
        yield "outList = []"
        yield "if inLength > 0:"

        if self.amountType == "AMOUNT":
            yield "    outLength = inLength * amount"
        elif self.amountType == "LENGTH":
            yield "    outLength = length"
        elif self.amountType == "LENGTH_FLOOR":
            yield "    outLength = int(math.floor(length / inLength) * inLength)"
        elif self.amountType == "LENGTH_CEIL":
            yield "    outLength = int(math.ceil(length / inLength) * inLength)"
        yield "    outLength = max(0, outLength)"

        if self.repetitionType == "LOOP":
                yield "    elementIterator = itertools.cycle(inList)"
        elif self.repetitionType == "PING_PONG":
                yield "    elementIterator = itertools.cycle(inList + inList[::-1])"

        if makeCopies:
            yield ("    elementIterator = ({} for element in elementIterator)"
                   .format(copyExpression.replace("value", "element")))

        yield "    outList = list(itertools.islice(elementIterator, outLength))"

    def getUsedModules(self):
        return ["itertools", "math"]

    def edit(self):
        listDataType = self.getWantedDataType()
        self.assignType(listDataType)

    def assignListDataType(self, listDataType):
        self.assignedType = listDataType

    def getWantedDataType(self):
        listInput = self.inputs["List"].dataOrigin
        listOutputs = self.outputs["List"].dataTargets

        if listInput is not None: return listInput.dataType
        if len(listOutputs) == 1: return listOutputs[0].dataType
        return self.inputs["List"].dataType

    def assignType(self, listDataType):
        if not isList(listDataType): return
        if listDataType == self.assignedType: return
        self.assignedType = listDataType
