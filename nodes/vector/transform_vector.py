import bpy
from ... base_types.node import AnimationNode

class TransformVectorNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_TransformVectorNode"
    bl_label = "Transform Vector"

    def create(self):
        self.newInput("Vector", "Vector", "vector")
        self.newInput("Matrix", "Matrix", "matrix")
        self.newOutput("Vector", "Vector", "transformedVector")

    def getExecutionCode(self):
        return "transformedVector = matrix * vector"
