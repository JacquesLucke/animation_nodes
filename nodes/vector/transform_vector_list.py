import bpy
from ... math import transformVector3DListAsPoints
from ... base_types.node import AnimationNode

class TransformVectorListNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_TransformVectorListNode"
    bl_label = "Transform Vector List"

    def create(self):
        self.newInput("Vector List", "Vector List", "vectors", dataIsModified = True)
        self.newInput("Matrix", "Matrix", "matrix")
        self.newOutput("Vector List", "Vectors List", "vectors")

    def execute(self, vectors, matrix):
        transformVector3DListAsPoints(vectors, matrix)
        return vectors
