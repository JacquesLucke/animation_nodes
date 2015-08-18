import bpy
from ... base_types.node import AnimationNode

class SeparateVector(bpy.types.Node, AnimationNode):
    bl_idname = "an_SeparateVector"
    bl_label = "Separate Vector"
    isDetermined = True

    def create(self):
        self.inputs.new("an_VectorSocket", "Vector", "vector")
        self.outputs.new("an_FloatSocket", "X", "x")
        self.outputs.new("an_FloatSocket", "Y", "y")
        self.outputs.new("an_FloatSocket", "Z", "z")

    def getExecutionCode(self):
        return "x, y, z = vector.xyz"
