import bpy
from ... base_types.node import AnimationNode

class VectorDistanceNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_VectorDistanceNode"
    bl_label = "Vector Distance"

    def create(self):
        self.newInput("Vector", "A", "a")
        self.newInput("Vector", "B", "b")
        self.newOutput("Float", "Distance", "distance")

    def getExecutionCode(self):
        return "distance = (a - b).length"
