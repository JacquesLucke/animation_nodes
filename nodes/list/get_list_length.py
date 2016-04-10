import bpy
from ... base_types.node import AnimationNode

class GetListLengthNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GetListLengthNode"
    bl_label = "Get List Length"

    def create(self):
        self.newInput("an_GenericSocket", "List", "list")
        self.newOutput("an_IntegerSocket", "Length", "length")

    def getExecutionCode(self):
        return ("try: length = len(list)",
                "except: length = 0")
