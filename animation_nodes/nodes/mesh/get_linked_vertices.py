import bpy
from ... base_types import AnimationNode
from ... data_structures import LongList

class GetLinkedVerticesNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_GetLinkedVerticesNode"
    bl_label = "Get Linked Vertices"
    errorHandlingType = "EXCEPTION"

    def create(self):
        self.newInput("Mesh", "Mesh", "mesh")
        self.newInput("Integer", "Vextex Index", "vertexIndex")

        self.newOutput("Integer List", "Vertices", "vertexIndices")
        self.newOutput("Integer List", "Edges", "edgeIndices")
        self.newOutput("Integer", "Amount", "amount")

    def execute(self, mesh, vertexIndex):
        if mesh is None:
            return LongList(), LongList(), 0
        if vertexIndex < 0 or vertexIndex >= len(mesh.vertices):
            self.raiseErrorMessage("Vertex Index is out of range.")

        return mesh.getVertexLinkedVertices(vertexIndex)
