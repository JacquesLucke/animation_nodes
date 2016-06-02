import bpy
from ... base_types.node import AnimationNode

class CreateEdgeIndicesNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_CreateEdgeIndicesNode"
    bl_label = "Create Edge Indices"

    def create(self):
        self.newInput("Integer", "Index 1", "index1").value = 0
        self.newInput("Integer", "Index 2", "index2").value = 1
        self.newOutput("Edge Indices", "Edge Indices", "edgeIndices")

    def getExecutionCode(self):
        return "edgeIndices = (index1, index2)"
