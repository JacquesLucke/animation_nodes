import bpy
from bpy.props import *
from ... sockets.info import isList
from ... base_types import AnimationNode, AutoSelectDataType
from ... data_structures cimport DoubleList, LongLongList, BooleanList

ctypedef fused NumberList:
    DoubleList
    LongLongList

class NumberToBooleanNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_NumberToBooleanNode"
    bl_label = "Number to Boolean"

    sourceType = StringProperty(default = "Integer", update = AnimationNode.updateSockets)

    def create(self):
        if isList(self.sourceType):
            self.newInput(self.sourceType, "Numbers", "numbers", alternativeIdentifier = "number")
        else:
            self.newInput(self.sourceType, "Number", "number", alternativeIdentifier = "numbers")

        self.newOutputGroup(isList(self.sourceType),
            ("Boolean", "Boolean", "boolean"),
            ("Boolean List", "Booleans", "booleans"))

        self.newSocketEffect(AutoSelectDataType("sourceType", [self.inputs[0]],
            use = ["Integer", "Float", "Integer List", "Float List"]))

    def getExecutionCode(self):
        if isList(self.sourceType):
            return "booleans = self.convertToBooleanList(numbers)"
        else:
            return "boolean = bool(number)"

    def convertToBooleanList(self, NumberList inList):
        cdef BooleanList outList = BooleanList(length = inList.length)
        cdef long i
        for i in range(len(inList)):
            outList.data[i] = inList.data[i] != 0
        return outList
