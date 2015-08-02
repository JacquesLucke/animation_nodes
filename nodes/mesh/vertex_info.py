import bpy
from ... base_types.node import AnimationNode

class VertexInfo(bpy.types.Node, AnimationNode):
    bl_idname = "mn_VertexInfo"
    bl_label = "Vertex Info"

    inputNames = { "Vertex" : "vertex" }

    outputNames = { "Location" : "location",
                    "Normal" : "normal",
                    "Group Weights" : "groupWeights" }

    def create(self):
        self.inputs.new("mn_VertexSocket", "Vertex")
        self.outputs.new("mn_VectorSocket", "Location")
        self.outputs.new("mn_VectorSocket", "Normal")
        self.outputs.new("mn_FloatListSocket", "Group Weights")

    def execute(self, vertex):
        return vertex.location, vertex.normal, vertex.groupWeights
