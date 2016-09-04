import bpy
from ... base_types import AnimationNode

class SeparateVectorNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SeparateVectorNode"
    bl_label = "Separate Vector"

    def create(self):
        self.newInput("Vector", "Vector", "vector")
        self.newOutput("Float", "X", "x")
        self.newOutput("Float", "Y", "y")
        self.newOutput("Float", "Z", "z")

    def getExecutionCode(self):
        isLinked = self.getLinkedOutputsDict()
        if isLinked["x"]: yield "x = vector[0]"
        if isLinked["y"]: yield "y = vector[1]"
        if isLinked["z"]: yield "z = vector[2]"
