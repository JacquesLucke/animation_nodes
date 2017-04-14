from libc.string cimport memcpy

from ... data_structures cimport (
    DoubleList,
    Vector3DList,
    Matrix4x4List,
    EdgeIndicesList,
    PolygonIndicesList
)

from ... math cimport (
    Vector3, distanceVec3, transformVec3AsPoint_InPlace,
    Matrix4
)

def createEdges(Vector3DList points1, Vector3DList points2):
    assert(len(points1) == len(points2))

    cdef Vector3DList newPoints = Vector3DList(length = len(points1) * 2)
    cdef EdgeIndicesList edges = EdgeIndicesList(length = len(points1))
    cdef Py_ssize_t i

    for i in range(len(points1)):
        newPoints.data[2 * i + 0] = points1.data[i]
        newPoints.data[2 * i + 1] = points2.data[i]
        edges.data[i].v1 = 2 * i + 0
        edges.data[i].v2 = 2 * i + 1

    return newPoints, edges

def calculateEdgeLengths(Vector3DList vertices, EdgeIndicesList edges):
    if len(edges) == 0:
        return DoubleList()

    if edges.getMaxIndex() >= len(vertices):
        raise Exception("Edges are invalid")

    cdef DoubleList distances = DoubleList(length = len(edges))
    cdef Py_ssize_t i
    cdef Vector3 *v1
    cdef Vector3 *v2
    for i in range(len(edges)):
        v1 = vertices.data + edges.data[i].v1
        v2 = vertices.data + edges.data[i].v2
        distances.data[i] = distanceVec3(v1, v2)
    return distances

def transformPolygons(Vector3DList vertices, PolygonIndicesList polygons, Matrix4x4List matrices):
    cdef:
        Matrix4 *_matrices = matrices.data
        Matrix4 *matrix
        long i, j
        long start, length
        Vector3 *_vertices = vertices.data
        unsigned int *_polyStarts = polygons.polyStarts.data
        unsigned int *_polyLengths = polygons.polyLengths.data
        unsigned int *_indices = polygons.indices.data

    for i in range(matrices.length):
        matrix = _matrices + i
        start = _polyStarts[i]
        length = _polyLengths[i]
        for j in range(length):
            transformVec3AsPoint_InPlace(_vertices + _indices[start + j], matrix)

def separatePolygons(Vector3DList oldVertices, PolygonIndicesList oldPolygons):
    cdef Vector3DList newVertices
    cdef PolygonIndicesList newPolygons

    newVertices = Vector3DList(length = oldPolygons.indices.length)
    newPolygons = PolygonIndicesList(indicesAmount = oldPolygons.indices.length,
                                     polygonAmount = oldPolygons.getLength())

    memcpy(newPolygons.polyStarts.data,
           oldPolygons.polyStarts.data,
           oldPolygons.polyStarts.length * oldPolygons.polyStarts.getElementSize())

    memcpy(newPolygons.polyLengths.data,
           oldPolygons.polyLengths.data,
           oldPolygons.polyLengths.length * oldPolygons.polyLengths.getElementSize())

    cdef:
        long i
        Vector3* _oldVertices = oldVertices.data
        Vector3* _newVertices = newVertices.data
        unsigned int* _oldIndices = oldPolygons.indices.data
        unsigned int* _newIndices = newPolygons.indices.data

    for i in range(oldPolygons.indices.length):
        _newIndices[i] = i
        _newVertices[i] = _oldVertices[_oldIndices[i]]

    return newVertices, newPolygons
