import bpy
from bpy.props import *
from ... sockets.info import isList
from ... events import propertyChanged
from ... algorithms.lists import repeatElements
from ... data_structures import VirtualLongList
from ... base_types import AnimationNode, VectorizedSocket, ListTypeSelectorSocket

class RepeatListElementsNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_RepeatListElementsNode"
    bl_label = "Repeat List Elements"
    errorHandlingType = "EXCEPTION"

    useList: VectorizedSocket.newProperty()
    assignedType: ListTypeSelectorSocket.newProperty(default = "Float List")
    makeElementCopies: BoolProperty(name = "Make Element Copies", default = True,
        description = "Insert copies of the original elements",
        update = propertyChanged)

    def create(self):
        prop = ("assignedType", "LIST")

        self.newInput(ListTypeSelectorSocket(
            "List", "inList", "LIST", prop, dataIsModified = True))

        self.newInput(VectorizedSocket("Integer", "useList",
            ("Amount", "amount", dict(value = 3, minValue = 0)),
            ("Amounts", "amounts")))

        self.newOutput(ListTypeSelectorSocket(
            "Repeated List", "repeatedList", "LIST", prop))

    def drawAdvanced(self, layout):
        layout.prop(self, "makeElementCopies")
        self.invokeSelector(layout, "DATA_TYPE", "assignListDataType",
            dataTypes = "LIST", text = "Change Type", icon = "TRIA_RIGHT")

    def execute(self, inList, amounts):
        if self.useList:
            if amounts.containsValueLowerThan(0):
                self.raiseErrorMessage("The amounts list can not contain a negative amount.")
        else:
            if amounts < 0:
                self.raiseErrorMessage("The amount can not be negative.")

        amounts = VirtualLongList.create(amounts, 0).materialize(len(inList))
        return repeatElements(self.assignedType, inList, amounts, self.makeElementCopies)

    def assignListDataType(self, listDataType):
        if not isList(listDataType): return
        if listDataType == self.assignedType: return
        self.assignedType = listDataType
        self.refresh()
