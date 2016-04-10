import bpy
from ... base_types.node import AnimationNode

class VectorLengthNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_VectorLengthNode"
    bl_label = "Vector Length"

    def create(self):
        self.newInput("an_VectorSocket", "Vector", "vector")
        self.newOutput("an_FloatSocket", "Length", "length")

    def getExecutionCode(self):
        return "length = vector.length"
