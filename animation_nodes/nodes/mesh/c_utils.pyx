cimport cython
from libc.string cimport memcpy

from ... data_structures cimport (
    DoubleList,
    Vector3DList,
    Matrix4x4List,
    EdgeIndicesList,
    PolygonIndicesList
)

from ... math cimport (
    Vector3, Matrix4,
    scaleVec3, subVec3, crossVec3, distanceVec3,
    transformVec3AsPoint_InPlace, normalizeVec3_InPlace, scaleVec3_Inplace
)

# Edge Operations
###########################################

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


# Polygon Operations
######################################################

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


# Extract Polygon Transforms
###########################################

def extractPolygonTransforms(Vector3DList vertices, PolygonIndicesList polygons,
                             bint calcNormal = True, bint calcInverted = False):
    if not calcNormal and not calcInverted:
        return None

    cdef Py_ssize_t i
    cdef Vector3 center, normal, tangent, bitangent
    cdef Matrix4x4List transforms, invertedTransforms

    if calcNormal:
        transforms = Matrix4x4List(length = polygons.getLength())
    if calcInverted:
        invertedTransforms = Matrix4x4List(length = polygons.getLength())

    for i in range(transforms.length):
        extractPolygonData(
            vertices.data,
            polygons.indices.data + polygons.polyStarts.data[i],
            polygons.polyLengths.data[i],
            &center, &normal, &tangent)

        normalizeVec3_InPlace(&normal)
        normalizeVec3_InPlace(&tangent)
        crossVec3(&bitangent, &tangent, &normal)
        scaleVec3_Inplace(&bitangent, -1)

        if calcNormal:
            createMatrix(transforms.data + i, &center, &normal, &tangent, &bitangent)
        if calcInverted:
            createInvertedMatrix(invertedTransforms.data + i, &center, &normal, &tangent, &bitangent)

    if calcNormal and calcInverted:
        return transforms, invertedTransforms
    elif calcNormal:
        return transforms
    else:
        return invertedTransforms

@cython.cdivision(True)
cdef void extractPolygonData(Vector3 *vertices,
                        unsigned int *indices, unsigned int vertexAmount,
                        Vector3 *center, Vector3 *normal, Vector3 *tangent):
    # Center
    cdef Py_ssize_t i
    cdef Vector3 *current
    cdef Vector3 sum = {"x" : 0, "y" : 0, "z" : 0}

    for i in range(vertexAmount):
        current = vertices + indices[i]
        sum.x += current.x
        sum.y += current.y
        sum.z += current.z
    scaleVec3(center, &sum, 1 / <float>vertexAmount)

    # Normal
    cdef Vector3 a, b
    subVec3(&a, vertices + indices[1], vertices + indices[0])
    subVec3(&b, vertices + indices[2], vertices + indices[0])
    crossVec3(normal, &a, &b)

    # Tangent
    tangent[0] = a

cdef void createMatrix(Matrix4 *m, Vector3 *center, Vector3 *normal, Vector3 *tangent, Vector3 *bitangent):
    m.a11, m.a12, m.a13, m.a14 = tangent.x, bitangent.x, normal.x, center.x
    m.a21, m.a22, m.a23, m.a24 = tangent.y, bitangent.y, normal.y, center.y
    m.a31, m.a32, m.a33, m.a34 = tangent.z, bitangent.z, normal.z, center.z
    m.a41, m.a42, m.a43, m.a44 = 0, 0, 0, 1

cdef void createInvertedMatrix(Matrix4 *m, Vector3 *center, Vector3 *normal, Vector3 *tangent, Vector3 *bitangent):
    m.a11, m.a12, m.a13 = tangent.x,   tangent.y,   tangent.z,
    m.a21, m.a22, m.a23 = bitangent.x, bitangent.y, bitangent.z
    m.a31, m.a32, m.a33 = normal.x,    normal.y,    normal.z
    m.a41, m.a42, m.a43, m.a44 = 0, 0, 0, 1

    m.a14 = -(tangent.x   * center.x + tangent.y   * center.y + tangent.z   * center.z)
    m.a24 = -(bitangent.x * center.x + bitangent.y * center.y + bitangent.z * center.z)
    m.a34 = -(normal.x    * center.x + normal.y    * center.y + normal.z    * center.z)
