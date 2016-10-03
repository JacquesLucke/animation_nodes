import bpy
from libc.string cimport memcpy
from ... base_types import AnimationNode
from ... math cimport transformVec3AsPoint
from ... data_structures cimport (MeshData,
            Vector3DList, Matrix4x4List, EdgeIndicesList, PolygonIndicesList)

class ReplicateMeshDataNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ReplicateMeshDataNode"
    bl_label = "Replicate Mesh Data"

    def create(self):
        self.newInput("Mesh Data", "Mesh Data", "sourceMeshData")
        self.newInput("Matrix List", "Matrices", "matrices")
        self.newOutput("Mesh Data", "Mesh Data", "outMeshData")

    def execute(self, MeshData source, Matrix4x4List matrices):
        cdef:
            Py_ssize_t i, j, offset
            Py_ssize_t amount = len(matrices)
            Py_ssize_t vertexAmount, edgeAmount, polygonAmount, polygonIndicesAmount
            Vector3DList oldVertices, newVertices
            EdgeIndicesList oldEdges, newEdges
            PolygonIndicesList oldPolygons, newPolygons

        oldVertices = source.vertices
        oldEdges = source.edges
        oldPolygons = source.polygons

        vertexAmount = len(oldVertices)
        edgeAmount = len(oldEdges)
        polygonAmount = len(oldPolygons)
        polygonIndicesAmount = len(oldPolygons.indices)

        newVertices = Vector3DList(length = amount * vertexAmount)
        newEdges = EdgeIndicesList(length = amount * edgeAmount)
        newPolygons = PolygonIndicesList(indicesAmount = amount * polygonIndicesAmount,
                                         polygonAmount = amount * polygonAmount)

        # Vertices
        for i in range(amount):
            offset = i * vertexAmount
            for j in range(vertexAmount):
                transformVec3AsPoint(newVertices.data + offset + j,
                                     oldVertices.data + j,
                                     matrices.data + i)

        # Edges
        for i in range(amount):
            offset = i * edgeAmount
            for j in range(edgeAmount):
                newEdges.data[offset + j].v1 = oldEdges.data[j].v1 + vertexAmount * i
                newEdges.data[offset + j].v2 = oldEdges.data[j].v2 + vertexAmount * i

        # Polygon Indices
        for i in range(amount):
            offset = i * polygonIndicesAmount
            for j in range(polygonIndicesAmount):
                newPolygons.indices.data[offset + j] = oldPolygons.indices.data[j] + vertexAmount * i
        # Polygon Starts
        for i in range(amount):
            offset = i * polygonAmount
            for j in range(polygonAmount):
                newPolygons.polyStarts.data[offset + j] = oldPolygons.polyStarts.data[j] + polygonIndicesAmount * i
        # Polygon Lengths
        for i in range(amount):
            memcpy(newPolygons.polyLengths.data + i * polygonAmount,
                   oldPolygons.polyLengths.data,
                   sizeof(unsigned int) * polygonAmount)

        return MeshData(newVertices, newEdges, newPolygons)
