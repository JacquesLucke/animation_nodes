import bpy
from ... base_types.node import AnimationNode

class TransformVertex(bpy.types.Node, AnimationNode):
    bl_idname = "mn_TransformVertex"
    bl_label = "Transform Vertex"

    inputNames = { "Vertex" : "vertex",
                   "Matrix" : "matrix" }

    outputNames = { "Vertex" : "vertex" }

    def create(self):
        self.inputs.new("mn_VertexSocket", "Vertex")
        self.inputs.new("mn_MatrixSocket", "Matrix")
        self.outputs.new("mn_VertexSocket", "Vertex")

    def execute(self, vertex, matrix):
        vertex.location = matrix * vertex.location
        return vertex
