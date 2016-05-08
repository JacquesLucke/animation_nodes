import bpy
from ... base_types.node import AnimationNode

class IntegerListToFloatListNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_IntegerListToFloatListNode"
    bl_label = "Integer List to Float List"

    def create(self):
        self.newInput("Integer List", "Integer List", "integerList")
        self.newOutput("Float List", "Float List", "floatList")

    def getExecutionCode(self):
        return "floatList = algorithms.lists.convert.toDoubleList(integerList)"
