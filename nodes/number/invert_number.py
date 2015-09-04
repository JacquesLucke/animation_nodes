import bpy
from ... base_types.node import AnimationNode

class InvertNumberNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_InvertNumberNode"
    bl_label = "Invert Number"

    def create(self):
        self.inputs.new("an_FloatSocket", "Number", "number")
        self.outputs.new("an_FloatSocket", "Number", "invertedNumber")

    def getExecutionCode(self):
        return "invertedNumber = -number"
