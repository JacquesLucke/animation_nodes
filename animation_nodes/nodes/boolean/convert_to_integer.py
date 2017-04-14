import bpy
from ... base_types import VectorizedNode
from . c_utils import convert_BooleanList_to_LongList

class BooleanToIntegerNode(bpy.types.Node, VectorizedNode):
    bl_idname = "an_BooleanToIntegerNode"
    bl_label = "Boolean to Integer"

    useList = VectorizedNode.newVectorizeProperty()

    def create(self):
        self.newVectorizedInput("Boolean", "useList",
            ("Boolean", "boolean"), ("Booleans", "booleans"))
        self.newVectorizedOutput("Integer", "useList",
            ("Number", "number"), ("Numbers", "numbers"))

    def getExecutionCode(self):
        if self.useList:
            return "numbers = self.convertToNumberList(booleans)"
        else:
            return "number = int(boolean)"

    def convertToNumberList(self, booleans):
        return convert_BooleanList_to_LongList(booleans)
