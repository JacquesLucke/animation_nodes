import bpy
from ... base_types.node import AnimationNode

class SeparateMeshDataNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SeparateMeshDataNode"
    bl_label = "Separate Mesh Data"

    def create(self):
        self.newInput("an_MeshDataSocket", "Mesh Data", "meshData").dataIsModified = True
        self.newOutput("an_VectorListSocket", "Vertex Locations", "vertexLocations")
        self.newOutput("an_EdgeIndicesListSocket", "Edges Indices", "edgesIndices")
        self.newOutput("an_PolygonIndicesListSocket", "Polygons Indices", "polygonsIndices")

    def execute(self, meshData):
        return meshData.vertices, meshData.edges, meshData.polygons
