import bpy
from ... base_types.node import AnimationNode

class SeparateMeshData(bpy.types.Node, AnimationNode):
    bl_idname = "an_SeparateMeshData"
    bl_label = "Separate Mesh Data"

    def create(self):
        self.inputs.new("an_MeshDataSocket", "Mesh Data", "meshData")
        self.outputs.new("an_VectorListSocket", "Vertex Locations", "vertexLocations")
        self.outputs.new("an_EdgeIndicesListSocket", "Edges Indices", "edgesIndices")
        self.outputs.new("an_PolygonIndicesListSocket", "Polygons Indices", "polygonsIndices")

    def execute(self, meshData):
        return meshData.vertices, meshData.edges, meshData.polygons
