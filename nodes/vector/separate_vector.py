import bpy
from ... base_types.node import AnimationNode

class SeparateVectorNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SeparateVectorNode"
    bl_label = "Separate Vector"

    def create(self):
        self.newInput("Vector", "Vector", "vector")
        self.newOutput("Float", "X", "x")
        self.newOutput("Float", "Y", "y")
        self.newOutput("Float", "Z", "z")

    def getExecutionCode(self):
        return "x, y, z = vector.xyz"
