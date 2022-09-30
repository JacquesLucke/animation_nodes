import bpy
from ... base_types import AnimationNode

class ConvertToTextNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_ConvertToTextNode"
    bl_label = "Convert to Text"

    def create(self):
        self.newInput("Generic", "Data", "data")
        self.newOutput("Text", "Text", "text")

    def getExecutionCode(self, required):
        return "text = str(data)"
