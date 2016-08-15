import bpy
from ... base_types.node import AnimationNode

class IsNoneNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_IsNoneNode"
    bl_label = "Is None Boolean"

    def create(self):
        self.newInput("Generic", "Input", "input")
        self.newOutput("Boolean", "Output", "output")

    def getExecutionCode(self):
        return "output = input is None"
