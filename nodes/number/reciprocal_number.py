import bpy
from ... base_types.node import AnimationNode

class ReciprocalNumberNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ReciprocalNumberNode"
    bl_label = "Reciprocal Number"

    def create(self):
        self.inputs.new("an_FloatSocket", "Number", "number").value = 1
        self.outputs.new("an_FloatSocket", "Number", "reciprocalNumber")

    def getExecutionCode(self):
        return "reciprocalNumber = 1 / number if number != 0 else 0"
