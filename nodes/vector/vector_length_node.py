import bpy
from ... base_types.node import AnimationNode

class VectorLengthNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_VectorLengthNode"
    bl_label = "Vector Length"
    isDetermined = True

    inputNames = { "Vector" : "vector" }
    outputNames = { "Length" : "length" }

    def create(self):
        self.inputs.new("an_VectorSocket", "Vector")
        self.outputs.new("an_FloatSocket", "Length")

    def getExecutionCode(self):
        return "$length$ = %vector%.length"
