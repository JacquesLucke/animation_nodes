import bpy
from ... base_types.node import AnimationNode

class VertexInfo(bpy.types.Node, AnimationNode):
    bl_idname = "an_VertexInfo"
    bl_label = "Vertex Info"

    inputNames = { "Vertex" : "vertex" }

    outputNames = { "Location" : "location",
                    "Normal" : "normal",
                    "Group Weights" : "groupWeights" }

    def create(self):
        self.inputs.new("an_VertexSocket", "Vertex")
        self.outputs.new("an_VectorSocket", "Location")
        self.outputs.new("an_VectorSocket", "Normal")
        self.outputs.new("an_FloatListSocket", "Group Weights")

    def execute(self, vertex):
        return vertex.location, vertex.normal, vertex.groupWeights
