import bpy
from bpy.props import *
from ... base_types import VectorizedNode
from . list_utils import convert_DoubleList_to_BooleanList

class NumberToBooleanNode(bpy.types.Node, VectorizedNode):
    bl_idname = "an_NumberToBooleanNode"
    bl_label = "Number to Boolean"

    useList = VectorizedNode.newVectorizeProperty()

    def create(self):
        self.newVectorizedInput("Float", "useList",
            ("Number", "number"), ("Numbers", "numbers"))

        self.newVectorizedOutput("Boolean", "useList",
            ("Boolean", "boolean"), ("Booleans", "booleans"))

    def getExecutionCode(self):
        if self.useList:
            return "booleans = self.convertToBooleanList(numbers)"
        else:
            return "boolean = bool(number)"

    def convertToBooleanList(self, inList):
        return convert_DoubleList_to_BooleanList(inList)
