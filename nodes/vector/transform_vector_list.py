import bpy
from ... base_types.node import AnimationNode

class TransformVectorListNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_TransformVectorListNode"
    bl_label = "Transform Vector List"

    def create(self):
        self.newInput("Vector List", "Vector List", "vectors")
        self.newInput("Matrix", "Matrix", "matrix")
        self.newOutput("Vector List", "Vectors List", "transformedVectors")

    def getExecutionCode(self):
        return "transformedVectors = [matrix * vector for vector in vectors]"
