import bpy
from ... base_types.node import AnimationNode

class SeparateMeshData(bpy.types.Node, AnimationNode):
    bl_idname = "an_SeparateMeshData"
    bl_label = "Separate Mesh Data"

    inputNames = { "Mesh Data" : "meshData" }

    outputNames = { "Vertex Locations" : "vertexLocations",
                    "Edges Indices" : "edgesIndices",
                    "Polygons Indices" : "polygonsIndices" }

    def create(self):
        self.inputs.new("an_MeshDataSocket", "Mesh Data")
        self.outputs.new("an_VectorListSocket", "Vertex Locations")
        self.outputs.new("an_EdgeIndicesListSocket", "Edges Indices")
        self.outputs.new("an_PolygonIndicesListSocket", "Polygons Indices")

    def execute(self, meshData):
        return meshData.vertices, meshData.edges, meshData.polygons
