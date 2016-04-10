import bpy
from ... base_types.node import AnimationNode

class TransformVectorNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_TransformVectorNode"
    bl_label = "Transform Vector"

    def create(self):
        self.newInput("an_VectorSocket", "Vector", "vector")
        self.newInput("an_MatrixSocket", "Matrix", "matrix")
        self.newOutput("an_VectorSocket", "Vector", "transformedVector")

    def getExecutionCode(self):
        return "transformedVector = matrix * vector"
