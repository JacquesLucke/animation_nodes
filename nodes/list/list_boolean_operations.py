import bpy
import itertools
from bpy.props import *
from ... tree_info import keepNodeLinks
from ... events import executionCodeChanged
from ... sockets.info import toIdName, isList
from ... base_types.node import AnimationNode

operationItems = [
    ("UNION", "Union", "Elements that are at least in one of both lists", "NONE", 0),
    ("INTERSECTION", "Intersection", "Elements that are in both lists", "NONE", 1),
    ("DIFFERENCE", "Difference", "Elements that are in list 1 but not in list 2", "NONE", 2),
    ("SYMMETRIC_DIFFERENCE", "Symmetric Difference", "Elements that are in list 1 or in list 2 but not in both", "NONE", 3) ]

class ListBooleanOperationsNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ListBooleanOperationsNode"
    bl_label = "List Boolean Operations"

    def assignedTypeChanged(self, context):
        self.listIdName = toIdName(self.assignedType)
        self.generateSockets()

    operation = EnumProperty(name = "Operation", default = "UNION",
        items = operationItems, update = executionCodeChanged)

    assignedType = StringProperty(update = assignedTypeChanged)
    listIdName = StringProperty()

    def create(self):
        self.assignedType = "Object List"

    def draw(self, layout):
        layout.prop(self, "operation", text = "")

    def getExecutionCode(self):
        op = self.operation
        # I don't use sets here to keep the order the elements come in
        if op == "UNION": return "outList = self.execute_Union(list1, list2)"
        if op == "INTERSECTION": return "outList = self.execute_Intersection(list1, list2)"
        if op == "DIFFERENCE": return "outList = self.execute_Difference(list1, list2)"
        if op == "SYMMETRIC_DIFFERENCE": return "outList = self.execute_SymmetricDifference(list1, list2)"

    def execute_Union(self, list1, list2):
        outList = []
        append = outList.append
        for element in itertools.chain(list1, list2):
            if element not in outList:
                append(element)
        return outList

    def execute_Intersection(self, list1, list2):
        outList = []
        append = outList.append
        for element in list1:
            if element not in outList:
                if element in list2:
                    append(element)
        return outList

    def execute_Difference(self, list1, list2):
        outList = []
        append = outList.append
        for element in list1:
            if element not in outList:
                if element not in list2:
                    append(element)
        return outList

    def execute_SymmetricDifference(self, list1, list2):
        # I could combine this out of the methods above but it would
        # propably be slower. Maybe someone can test this later.
        outList = []
        append = outList.append
        for element in list1:
            if element not in outList:
                if element not in list2:
                    append(element)
        for element in list2:
            if element not in outList:
                if element not in list1:
                    append(element)
        return outList

    def edit(self):
        listDataType = self.getWantedDataType()
        self.assignType(listDataType)

    def getWantedDataType(self):
        listInput1 = self.inputs[0].dataOrigin
        listInput2 = self.inputs[1].dataOrigin
        listOutputs = self.outputs[0].dataTargets

        if listInput1 is not None: return listInput1.dataType
        if listInput2 is not None: return listInput2.dataType
        if len(listOutputs) == 1: return listOutputs[0].dataType
        return self.inputs[0].dataType

    def assignType(self, listDataType):
        if not isList(listDataType): return
        if listDataType == self.assignedType: return
        self.assignedType = listDataType

    @keepNodeLinks
    def generateSockets(self):
        self.inputs.clear()
        self.outputs.clear()
        self.newInput(self.listIdName, "List 1", "list1").dataIsModified = True
        self.newInput(self.listIdName, "List 2", "list2").dataIsModified = True
        self.newOutput(self.listIdName, "List", "outList")
