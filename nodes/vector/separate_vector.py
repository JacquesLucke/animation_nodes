import bpy
from ... base_types.node import AnimationNode

class SeparateVectorNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SeparateVectorNode"
    bl_label = "Separate Vector"

    def create(self):
        self.newInput("an_VectorSocket", "Vector", "vector")
        self.newOutput("an_FloatSocket", "X", "x")
        self.newOutput("an_FloatSocket", "Y", "y")
        self.newOutput("an_FloatSocket", "Z", "z")

    def getExecutionCode(self):
        return "x, y, z = vector.xyz"
