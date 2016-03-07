import bpy
from bpy.props import *
from ... tree_info import keepNodeState
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode
from ... sockets.info import toIdName, toListIdName, toBaseDataType, isBase, isLimitedList, toGeneralListIdName

removeTypeItems = [
    ("FIRST_OCCURRENCE", "First Occurrence", "", "", 0),
    ("ALL_OCCURRENCES", "All Occurrences", "", "", 1),
    ("INDEX", "Index", "", "", 2) ]

class RemoveListElementNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_RemoveListElementNode"
    bl_label = "Remove List Element"

    def assignedTypeChanged(self, context):
        self.baseIdName = toIdName(self.assignedType)
        self.listIdName = toListIdName(self.assignedType)
        self.generateSockets()

    assignedType = StringProperty(update = assignedTypeChanged)
    baseIdName = StringProperty()
    listIdName = StringProperty()

    def removeTypeChanged(self, context):
        self.generateSockets()

    removeType = EnumProperty(name = "Remove Type", default = "FIRST_OCCURRENCE",
        items = removeTypeItems, update = removeTypeChanged)

    def create(self):
        self.assignedType = "Float"

    def draw(self, layout):
        layout.prop(self, "removeType", text = "")

    def drawAdvanced(self, layout):
        self.invokeSocketTypeChooser(layout, "assignListDataType",
            socketGroup = "LIST", text = "Change Type", icon = "TRIA_RIGHT")

    def getExecutionCode(self):
        yield "outList = inList"
        if self.removeType == "FIRST_OCCURRENCE":
            yield "try: inList.remove(element)"
            yield "except: pass"
        elif self.removeType == "ALL_OCCURRENCES":
            yield "outList = [e for e in inList if e != element]"
        elif self.removeType == "INDEX":
            yield "if 0 <= index < len(inList): del inList[index]"

    def edit(self):
        dataType = self.getWantedDataType()
        self.assignType(dataType)

    def getWantedDataType(self):
        listInput = self.inputs["List"].dataOrigin
        if listInput is not None:
            idName = listInput.bl_idname
            if isLimitedList(idName): idName = toGeneralListIdName(idName)
            return toBaseDataType(idName)

        if self.removeType in ("FIRST_OCCURRENCE", "ALL_OCCURRENCES"):
            elementInput = self.inputs["Element"].dataOrigin
            if elementInput is not None: return elementInput.dataType

        listOutputs = self.outputs["List"].dataTargets
        if len(listOutputs) == 1: return toBaseDataType(listOutputs[0].dataType)

        return toBaseDataType(self.inputs["List"].bl_idname)

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

        if self.removeType in ("FIRST_OCCURRENCE", "INDEX"):
            self.inputs.new(self.listIdName, "List", "inList").dataIsModified = True
        else:
            self.inputs.new(self.listIdName, "List", "inList")

        if self.removeType in ("FIRST_OCCURRENCE", "ALL_OCCURRENCES"):
            self.inputs.new(self.baseIdName, "Element", "element").defaultDrawType = "PREFER_PROPERTY"
        elif self.removeType == "INDEX":
            self.inputs.new("an_IntegerSocket", "Index", "index")

        self.outputs.new(self.listIdName, "List", "outList")
