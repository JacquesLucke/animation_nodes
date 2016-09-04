import bpy
from ... base_types import AnimationNode

class CreateEdgeIndicesNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_CreateEdgeIndicesNode"
    bl_label = "Create Edge Indices"

    def create(self):
        self.newInput("Integer", "Index 1", "index1", value = 0, minValue = 0)
        self.newInput("Integer", "Index 2", "index2", value = 1, minValue = 0)
        self.newOutput("Edge Indices", "Edge Indices", "edgeIndices")

    def getExecutionCode(self):
        return "edgeIndices = (max(index1, 0), max(index2, 0))"
