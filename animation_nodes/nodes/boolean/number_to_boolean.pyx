import bpy
from bpy.props import *
from ... data_structures cimport DoubleList, BooleanList
from ... base_types import AnimationNode, AutoSelectVectorization

class NumberToBooleanNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_NumberToBooleanNode"
    bl_label = "Number to Boolean"

    useList = BoolProperty(update = AnimationNode.refresh)

    def create(self):
        self.newInputGroup(self.useList,
            ("Float", "Number", "number"),
            ("Float List", "Numbers", "numbers"))

        self.newOutputGroup(self.useList,
            ("Boolean", "Boolean", "boolean"),
            ("Boolean List", "Booleans", "booleans"))

        vectorization = AutoSelectVectorization()
        vectorization.input(self, "useList", self.inputs[0])
        vectorization.output(self, "useList", self.outputs[0])
        self.newSocketEffect(vectorization)

    def getExecutionCode(self):
        if self.useList:
            return "booleans = self.convertToBooleanList(numbers)"
        else:
            return "boolean = bool(number)"

    def convertToBooleanList(self, DoubleList inList):
        cdef BooleanList outList = BooleanList(length = inList.length)
        cdef long i
        for i in range(len(inList)):
            outList.data[i] = inList.data[i] != 0
        return outList
