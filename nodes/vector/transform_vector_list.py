import bpy
from ... base_types.node import AnimationNode

class TransformVectorListNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_TransformVectorListNode"
    bl_label = "Transform Vector List"

    def create(self):
        self.newInput("an_VectorListSocket", "Vector List", "vectors")
        self.newInput("an_MatrixSocket", "Matrix", "matrix")
        self.newOutput("an_VectorListSocket", "Vector", "transformedVectors")

    def getExecutionCode(self):
        return "transformedVectors = [matrix * vector for vector in vectors]"
