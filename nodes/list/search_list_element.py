import bpy
from bpy.props import *
from ... tree_info import keepNodeLinks
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode
from ... sockets.info import isBase, toBaseDataType, toListDataType

class SearchListElementNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SearchListElementNode"
    bl_label = "Search List Element"

    def assignedTypeChanged(self, context):
        self.generateSockets()

    assignedType = StringProperty(update = assignedTypeChanged)

    def create(self):
        self.assignedType = "Float"
        self.newOutput("an_IntegerSocket", "First Index", "firstIndex")
        self.newOutput("an_IntegerListSocket", "All Indices", "allIndices")
        self.newOutput("an_IntegerSocket", "Occurrences", "occurrences")

    def drawAdvanced(self, layout):
        self.invokeSocketTypeChooser(layout, "assignListDataType",
            socketGroup = "LIST", text = "Change Type", icon = "TRIA_RIGHT")

    def getExecutionCode(self):
        isLinked = self.getLinkedOutputsDict()
        if not any(isLinked.values()): return

        if isLinked["allIndices"]:
            yield "allIndices = [i for i, element in enumerate(list) if element == search]"
            if isLinked["firstIndex"]:  yield "firstIndex = allIndices[0] if len(allIndices) > 0 else -1"
            if isLinked["occurrences"]: yield "occurrences = len(allIndices)"
        else:
            if isLinked["firstIndex"]:
                yield "try: firstIndex = list.index(search)"
                yield "except: firstIndex = -1"
            if isLinked["occurrences"]:
                yield "occurrences = list.count(search)"

    def edit(self):
        baseDataType = self.getWantedDataType()
        self.assignType(baseDataType)

    def getWantedDataType(self):
        listInput = self.inputs["List"].dataOrigin
        elementInput = self.inputs["Search"].dataOrigin

        if listInput is not None: return toBaseDataType(listInput.bl_idname)
        if elementInput is not None: return elementInput.dataType
        return self.inputs["Search"].dataType

    def assignListDataType(self, listDataType):
        self.assignType(toBaseDataType(listDataType))

    def assignType(self, baseDataType):
        if not isBase(baseDataType): return
        if baseDataType == self.assignedType: return
        self.assignedType = baseDataType

    @keepNodeLinks
    def generateSockets(self):
        self.inputs.clear()
        baseDataType = self.assignedType
        listDataType = toListDataType(self.assignedType)
        self.newInput(listDataType, "List", "list", dataIsModified  = True)
        self.newInput(baseDataType, "Search", "search", dataIsModified = True)
