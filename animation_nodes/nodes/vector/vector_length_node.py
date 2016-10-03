import bpy
from ... base_types import AnimationNode

class VectorLengthNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_VectorLengthNode"
    bl_label = "Vector Length"

    def create(self):
        self.newInput("Vector", "Vector", "vector")
        self.newOutput("Float", "Length", "length")

    def getExecutionCode(self):
        return "length = vector.length"
