import bpy
from ... base_types.node import AnimationNode

class ConvertToStringNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ConvertToStringNode"
    bl_label = "Convert to Text"

    def create(self):
        self.inputs.new("an_GenericSocket", "Data", "data")
        self.outputs.new("an_StringSocket", "Text", "text")

    def getExecutionCode(self):
        return "text = str(data)"
