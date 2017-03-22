import bpy
from bpy.props import *
from libc.string cimport memcpy
from ... math cimport transformVec3AsPoint, Vector3
from ... base_types import AnimationNode, AutoSelectDataType
from ... data_structures cimport (MeshData,
            Vector3DList, Matrix4x4List, EdgeIndicesList, PolygonIndicesList)

class ReplicateMeshDataNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ReplicateMeshDataNode"
    bl_label = "Replicate Mesh Data"

    transformationType = StringProperty(default = "Matrix List",
        update = AnimationNode.refresh)

    def create(self):
        self.newInput("Mesh Data", "Mesh Data", "sourceMeshData")
        self.newInput(self.transformationType, "Transformations", "transformations")
        self.newOutput("Mesh Data", "Mesh Data", "outMeshData")

        self.newSocketEffect(AutoSelectDataType("transformationType", [self.inputs[1]],
            use = ["Matrix List", "Vector List"], default = "Matrix List"))

    def execute(self, MeshData source, transformations):
        cdef:
            Py_ssize_t i, j, offset
            Py_ssize_t amount = len(transformations)
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

        newVertices = self.getTransformedVertices(oldVertices, transformations)
        newEdges = EdgeIndicesList(length = amount * edgeAmount)
        newPolygons = PolygonIndicesList(indicesAmount = amount * polygonIndicesAmount,
                                         polygonAmount = amount * polygonAmount)

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

    def getTransformedVertices(self, Vector3DList oldVertices, transformations):
        if isinstance(transformations, Vector3DList):
            return self.getTransformedVertices_VectorList(oldVertices, transformations)
        elif isinstance(transformations, Matrix4x4List):
            return self.getTransformedVertices_MatrixList(oldVertices, transformations)

    def getTransformedVertices_VectorList(self, Vector3DList oldVertices, Vector3DList transformations):
        cdef:
            Py_ssize_t i, j, offset
            Vector3DList newVertices = Vector3DList(oldVertices.length * transformations.length)
            Vector3* _oldVertices = oldVertices.data
            Vector3* _newVertices = newVertices.data
            Vector3* _transformations = transformations.data

        for i in range(transformations.length):
            offset = i * oldVertices.length
            for j in range(oldVertices.length):
                _newVertices[offset + j].x = _oldVertices[j].x + _transformations[i].x
                _newVertices[offset + j].y = _oldVertices[j].y + _transformations[i].y
                _newVertices[offset + j].z = _oldVertices[j].z + _transformations[i].z

        return newVertices

    def getTransformedVertices_MatrixList(self, Vector3DList oldVertices, Matrix4x4List transformations):
        cdef:
            Py_ssize_t i, j, offset
            Vector3DList newVertices = Vector3DList(oldVertices.length * transformations.length)

        for i in range(transformations.length):
            offset = i * oldVertices.length
            for j in range(oldVertices.length):
                transformVec3AsPoint(newVertices.data + offset + j,
                                     oldVertices.data + j,
                                     transformations.data + i)
        return newVertices
