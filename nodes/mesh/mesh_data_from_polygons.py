import bpy
from ... base_types.node import AnimationNode
from ... data_structures.mesh import MeshData

class MeshDataFromPolygonsNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MeshDataFromPolygonsNode"
    bl_label = "Mesh Data from Polygons"

    def create(self):
        self.inputs.new("an_PolygonListSocket", "Polygons", "polygons").dataIsModified = True
        self.outputs.new("an_MeshDataSocket", "Mesh Data", "meshData")

    def execute(self, polygons):
        vertices = []
        extendVertices = vertices.extend
        polygonIndices = []
        appendIndices = polygonIndices.append

        offset = 0
        for polygon in polygons:
            extendVertices(polygon.vertices)
            appendIndices([i + offset for i in range(len(polygon.vertices))])
            offset += len(polygon.vertices)

        return MeshData(vertices, [], polygonIndices)
