import bpy
from ... base_types import AnimationNode

class ConvertToFloatListNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ConvertToFloatListNode"
    bl_label = "Convert to Float List"

    def create(self):
        self.newInput("Integer List", "Integer List", "inList")
        self.newOutput("Float List", "Float List", "floatList")

    def getExecutionCode(self):
        return "floatList = DoubleList.fromValues(inList)"
