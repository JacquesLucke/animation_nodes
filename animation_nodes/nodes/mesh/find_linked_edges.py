import bpy
from ... base_types import AnimationNode
from ... data_structures import IntegerList

class FindLinkedEdgesNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_FindLinkedEdgesNode"
    bl_label = "Find Linked Edges"
    errorHandlingType = "EXCEPTION"

    def create(self):
        self.newInput("Mesh", "Mesh", "mesh")
        self.newInput("Integer", "Vextex Index", "vertexIndex")

        self.newOutput("Integer List", "Vertices", "vertexIndices")
        self.newOutput("Integer List", "Edges", "edgeIndices")

    def execute(self, mesh, vertexIndex):
        if mesh is None:
            return IntegerList(), IntegerList()
        if vertexIndex < 0 or vertexIndex >= len(mesh.vertices):
            self.raiseErrorMessage("Vertex Index is out of range.")

        return mesh.getVertexLinkedEdges(vertexIndex)
