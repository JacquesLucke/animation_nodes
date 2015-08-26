import bpy
from ... base_types.node import AnimationNode

class VertexInfoNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_VertexInfoNode"
    bl_label = "Vertex Info"

    def create(self):
        self.inputs.new("an_VertexSocket", "Vertex", "vertex").dataIsModified = True
        self.outputs.new("an_VectorSocket", "Location", "location")
        self.outputs.new("an_VectorSocket", "Normal", "normal")
        self.outputs.new("an_FloatListSocket", "Group Weights", "groupWeights")

    def execute(self, vertex):
        return vertex.location, vertex.normal, vertex.groupWeights
