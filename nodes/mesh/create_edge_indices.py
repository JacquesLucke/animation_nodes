import bpy
from ... base_types.node import AnimationNode

class CreateEdgeIndicesNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_CreateEdgeIndicesNode"
    bl_label = "Create Edge Indices"

    def create(self):
        self.newInput("an_IntegerSocket", "Index 1", "index1").value = 0
        self.newInput("an_IntegerSocket", "Index 2", "index2").value = 1
        self.newOutput("an_EdgeIndicesSocket", "Edge Indices", "edgeIndices")

    def getExecutionCode(self):
        return "edgeIndices = (index1, index2)"
