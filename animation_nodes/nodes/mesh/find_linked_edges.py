import bpy
from ... base_types import AnimationNode
from ... data_structures import LongList, EdgeIndicesList
from . c_utils import (
    getLinkedEdges
)

class FindLinkedEdgesNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_FindLinkedEdgesNode"
    bl_label = "Find Linked Edges"

    def create(self):
        self.newInput("Edge Indices List", "Edge Indices", "edgeIndicesList")
        self.newInput("Integer", "Vextex Index", "vextexIndex")

        self.newOutput("Integer List", "Vertices", "vextexIndices")
        self.newOutput("Integer List", "Edges", "edgeIndices")
        self.newOutput("Edge Indices List", "Edge Indices", "edgeIndicesListOut", hide = True)

    def execute(self, edgeIndicesList, vertexIndex):
        if len(edgeIndicesList) == 0: 
            return LongList(), LongList(), EdgeIndicesList()
        
        return getLinkedEdges(edgeIndicesList, vertexIndex)

    