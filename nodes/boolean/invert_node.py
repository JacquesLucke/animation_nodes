import bpy
from ... base_types.node import AnimationNode

class InvertNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_InvertNode"
    bl_label = "Invert Boolean"

    def create(self):
        self.newInput("Boolean", "Input", "input")
        self.newOutput("Boolean", "Output", "output")

    def getExecutionCode(self):
        return "output = not input"
