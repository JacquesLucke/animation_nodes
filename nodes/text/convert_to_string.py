import bpy
from ... base_types import AnimationNode

class ConvertToStringNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ConvertToStringNode"
    bl_label = "Convert to Text"

    def create(self):
        self.newInput("Generic", "Data", "data")
        self.newOutput("String", "Text", "text")

    def getExecutionCode(self):
        return "text = str(data)"
