import bpy
from ... base_types.node import AnimationNode

class VertexInfoNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_VertexInfoNode"
    bl_label = "Vertex Info"

    def create(self):
        self.newInput("Vertex", "Vertex", "vertex")
        self.newOutput("Vector", "Location", "location")
        self.newOutput("Vector", "Normal", "normal")
        self.newOutput("Float List", "Group Weights", "groupWeights")

    def getExecutionCode(self):
        isLinked = self.getLinkedOutputsDict()

        if isLinked["location"]: yield "location = vertex.location"
        if isLinked["normal"]: yield "normal = vertex.normal"
        if isLinked["groupWeights"]: yield "groupWeights = vertex.groupWeights"
