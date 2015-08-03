import bpy
from ... base_types.node import AnimationNode

class VectorDistanceNode(bpy.types.Node, AnimationNode):
    bl_idname = "mn_VectorDistanceNode"
    bl_label = "Vector Distance"
    isDetermined = True

    inputNames = { "A" : "a",
                   "B" : "b" }

    outputNames = { "Distance" : "distance" }

    def create(self):
        self.inputs.new("mn_VectorSocket", "A")
        self.inputs.new("mn_VectorSocket", "B")
        self.outputs.new("mn_FloatSocket", "Distance")

    def getExecutionCode(self):
        return "$distance$ = (%a% - %b%).length"
