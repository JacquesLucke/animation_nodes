import bpy
from ... base_types.node import AnimationNode

class VectorDistanceNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_VectorDistanceNode"
    bl_label = "Vector Distance"
    isDetermined = True

    def create(self):
        self.inputs.new("an_VectorSocket", "A", "a")
        self.inputs.new("an_VectorSocket", "B", "b")
        self.outputs.new("an_FloatSocket", "Distance", "distance")

    def getExecutionCode(self):
        return "distance = (a - b).length"
