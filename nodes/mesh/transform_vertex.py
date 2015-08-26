import bpy
from ... base_types.node import AnimationNode

class TransformVertexNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_TransformVertexNode"
    bl_label = "Transform Vertex"

    def create(self):
        self.inputs.new("an_VertexSocket", "Vertex", "vertex").dataIsModified = True
        self.inputs.new("an_MatrixSocket", "Matrix", "matrix")
        self.outputs.new("an_VertexSocket", "Vertex", "outVertex")

    def execute(self, vertex, matrix):
        vertex.location = matrix * vertex.location
        return vertex
