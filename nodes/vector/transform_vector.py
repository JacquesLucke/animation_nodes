import bpy
from ... base_types.node import AnimationNode

class TransformVector(bpy.types.Node, AnimationNode):
    bl_idname = "an_TransformVector"
    bl_label = "Transform Vector"

    def create(self):
        self.inputs.new("an_VectorSocket", "Vector", "vector")
        self.inputs.new("an_MatrixSocket", "Matrix", "matrix")
        self.outputs.new("an_VectorSocket", "Vector", "transformedVector")

    def getExecutionCode(self):
        return "transformedVector = matrix * vector"
