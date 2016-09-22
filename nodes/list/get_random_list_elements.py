import bpy
import random
from bpy.props import *
from ... events import propertyChanged
from ... sockets.info import isList, toBaseDataType
from ... base_types import AnimationNode, UpdateAssignedListDataType

selectionTypeItems = [
    ("SINGLE", "Single", "Select only one random element from the list", "NONE", 0),
    ("MULTIPLE", "Multiple", "Select multiple random elements from the list", "NONE", 1)]

class GetRandomListElementsNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GetRandomListElementsNode"
    bl_label = "Get Random List Elements"

    assignedType = StringProperty(update = AnimationNode.updateSockets, default = "Float List")

    selectionType = EnumProperty(name = "Select Type", default = "MULTIPLE",
        items = selectionTypeItems, update = AnimationNode.updateSockets)

    nodeSeed = IntProperty(update = propertyChanged)

    def setup(self):
        self.randomizeNodeSeed()

    def create(self):
        listDataType = self.assignedType
        baseDataType = toBaseDataType(listDataType)

        self.newInput("Integer", "Seed", "seed")
        self.newInput(listDataType, "List", "inList", dataIsModified = True)
        if self.selectionType == "SINGLE":
            self.newOutput(baseDataType, "Element", "outElement")
        elif self.selectionType == "MULTIPLE":
            self.newInput("Integer", "Amount", "amount", value = 3, minValue = 0)
            self.newOutput(listDataType, "List", "outList")

        self.newSocketEffect(UpdateAssignedListDataType("assignedType", [
            (self.inputs[1], "LIST"),
            (self.outputs[0], "BASE" if self.selectionType == "SINGLE" else "LIST")
        ], propertyType = "LIST"))

    def draw(self, layout):
        layout.prop(self, "selectionType", text = "")
        layout.prop(self, "nodeSeed", text = "Node Seed")

    def getExecutionCode(self):
        yield "random.seed(self.nodeSeed * 1245 + seed)"
        if self.selectionType == "SINGLE":
            yield "if len(inList) == 0: outElement = self.outputs['Element'].getDefaultValue()"
            yield "else: outElement = random.choice(inList)"
        elif self.selectionType == "MULTIPLE":
            yield "if len(inList) == 0: outList = []"
            yield "else: outList = random.sample(inList, min(amount, len(inList)))"

    def getUsedModules(self):
        return ["random"]

    def assignType(self, listDataType):
        if not isList(listDataType): return
        if listDataType == self.assignedType: return
        self.assignedType = listDataType

    def duplicate(self, sourceNode):
        self.randomizeNodeSeed()

    def randomizeNodeSeed(self):
        self.nodeSeed = int(random.random() * 100)
