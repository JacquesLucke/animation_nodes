import bpy
import random
from bpy.props import *
from ... events import propertyChanged
from ... tree_info import keepNodeState
from ... base_types.node import AnimationNode
from ... sockets.info import toIdName, isList, toBaseIdName, toListDataType

selectionTypeItems = [
    ("SINGLE", "Single", "Select only one random element from the list"),
    ("MULTIPLE", "Multiple", "Select multiple random elements from the list") ]

class GetRandomListElementsNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GetRandomListElementsNode"
    bl_label = "Get Random List Elements"

    def assignedTypeChanged(self, context):
        self.listIdName = toIdName(self.assignedType)
        self.generateSockets()

    def selectionTypeChanged(self, context):
        self.generateSockets()

    assignedType = StringProperty(update = assignedTypeChanged)
    listIdName = StringProperty()

    selectionType = EnumProperty(name = "Select Type", default = "MULTIPLE",
        items = selectionTypeItems, update = selectionTypeChanged)

    nodeSeed = IntProperty(update = propertyChanged)

    def create(self):
        self.assignedType = "Float List"
        self.randomizeNodeSeed()

    def draw(self, layout):
        layout.prop(self, "selectionType", text = "")
        layout.prop(self, "nodeSeed", text = "Node Seed")

    def getExecutionCode(self):
        yield "random.seed(self.nodeSeed * 1245 + seed)"
        if self.selectionType == "SINGLE":
            yield "if len(inList) == 0: outElement = self.outputs['Element'].getValue()"
            yield "else: outElement = random.choice(inList)"
        elif self.selectionType == "MULTIPLE":
            yield "if len(inList) == 0: outList = []"
            yield "else: outList = random.sample(inList, min(amount, len(inList)))"

    def getUsedModules(self):
        return ["random"]

    def edit(self):
        listDataType = self.getWantedDataType()
        self.assignType(listDataType)

    def getWantedDataType(self):
        listInput = self.inputs[1].dataOrigin
        if listInput is not None: return listInput.dataType

        if self.selectionType == "SINGLE":
            elementOutputs = self.outputs[0].dataTargets
            if len(elementOutputs) == 1: return toListDataType(elementOutputs[0].dataType)
        elif self.selectionType == "MULTIPLE":
            listOutputs = self.outputs[0].dataTargets
            if len(listOutputs) == 1: return listOutputs[0].dataType

        return self.inputs[0].dataType

    def assignType(self, listDataType):
        if not isList(listDataType): return
        if listDataType == self.assignedType: return
        self.assignedType = listDataType

    @keepNodeState
    def generateSockets(self):
        self.inputs.clear()
        self.outputs.clear()
        self.inputs.new("an_IntegerSocket", "Seed", "seed")
        self.inputs.new(self.listIdName, "List", "inList").dataIsModified = True
        if self.selectionType == "SINGLE":
            self.outputs.new(toBaseIdName(self.listIdName), "Element", "outElement")
        elif self.selectionType == "MULTIPLE":
            socket = self.inputs.new("an_IntegerSocket", "Amount", "amount")
            socket.minValue = 0
            socket.value = 3
            self.outputs.new(self.listIdName, "List", "outList")

    def duplicate(self, sourceNode):
        self.randomizeNodeSeed()

    def randomizeNodeSeed(self):
        self.nodeSeed = int(random.random() * 100)
