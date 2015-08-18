import bpy
from ... base_types.node import AnimationNode

class GetListLengthNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GetListLengthNode"
    bl_label = "Get List Length"

    def create(self):
        self.inputs.new("an_GenericSocket", "List", "list")
        self.outputs.new("an_IntegerSocket", "Length", "length")

    def getExecutionCodeLines(self):
        return ("try: length = len(list)",
                "except: length = 0")
