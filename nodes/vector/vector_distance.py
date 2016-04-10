import bpy
from ... base_types.node import AnimationNode

class VectorDistanceNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_VectorDistanceNode"
    bl_label = "Vector Distance"

    def create(self):
        self.newInput("an_VectorSocket", "A", "a")
        self.newInput("an_VectorSocket", "B", "b")
        self.newOutput("an_FloatSocket", "Distance", "distance")

    def getExecutionCode(self):
        return "distance = (a - b).length"
