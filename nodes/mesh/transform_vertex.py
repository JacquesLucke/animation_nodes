import bpy
from ... base_types.node import AnimationNode

class TransformVertex(bpy.types.Node, AnimationNode):
    bl_idname = "an_TransformVertex"
    bl_label = "Transform Vertex"

    inputNames = { "Vertex" : "vertex",
                   "Matrix" : "matrix" }

    outputNames = { "Vertex" : "vertex" }

    def create(self):
        self.inputs.new("an_VertexSocket", "Vertex")
        self.inputs.new("an_MatrixSocket", "Matrix")
        self.outputs.new("an_VertexSocket", "Vertex")

    def execute(self, vertex, matrix):
        vertex.location = matrix * vertex.location
        return vertex
