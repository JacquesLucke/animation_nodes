import bpy
from ... base_types.node import AnimationNode

class InvertNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_InvertNode"
    bl_label = "Invert Boolean"

    def create(self):
        self.newInput("an_BooleanSocket", "Input", "input")
        self.newOutput("an_BooleanSocket", "Output", "output")

    def getExecutionCode(self):
        return "output = not input"
