import bpy
from ... base_types.node import AnimationNode
from ... data_structures.mesh import MeshData

class MeshDataFromPolygonsNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MeshDataFromPolygonsNode"
    bl_label = "Mesh Data from Polygons"

    def create(self):
        self.newInput("Polygon List", "Polygons", "polygons", dataIsModified = True)
        self.newOutput("Mesh Data", "Mesh Data", "meshData")

    def execute(self, polygons):
        vertices = []
        extendVertices = vertices.extend
        polygonIndices = []
        appendIndices = polygonIndices.append

        offset = 0
        for polygon in polygons:
            extendVertices(polygon.vertexLocations)
            appendIndices([i + offset for i in range(len(polygon.vertexLocations))])
            offset += len(polygon.vertexLocations)

        return MeshData(vertices, [], polygonIndices)
