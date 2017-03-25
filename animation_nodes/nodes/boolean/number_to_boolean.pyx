import bpy
from bpy.props import *
from ... base_types import VectorizedNode
from ... data_structures cimport DoubleList, BooleanList

class NumberToBooleanNode(bpy.types.Node, VectorizedNode):
    bl_idname = "an_NumberToBooleanNode"
    bl_label = "Number to Boolean"

    useList = VectorizedNode.newVectorizeProperty()

    def createVectorized(self):
        self.newVectorizedInput("Float", "useList",
            ("Number", "number"), ("Numbers", "numbers"))

        self.newVectorizedOutput("Boolean", "useList",
            ("Boolean", "boolean"), ("Booleans", "booleans"))

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
