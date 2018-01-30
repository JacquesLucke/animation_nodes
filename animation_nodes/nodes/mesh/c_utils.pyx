# cython: profile=True
cimport cython
from libc.string cimport memcpy

from ... algorithms.mesh_generation.cylinder import getCylinderMesh

from ... data_structures cimport (
    LongList,
    DoubleList,
    UIntegerList,
    Vector2DList,
    Vector3DList,
    Matrix4x4List,
    EdgeIndicesList,
    PolygonIndicesList,
    CDefaultList,
    Mesh,
    VirtualLongList,
    VirtualDoubleList,
    EdgeIndices
)

from ... math cimport (
    Vector3, Matrix4,
    scaleVec3, subVec3, crossVec3, distanceVec3, lengthVec3, dotVec3,
    transformVec3AsPoint_InPlace, normalizeVec3_InPlace, scaleVec3_Inplace,
    normalizeLengthVec3_Inplace, transformVec3AsPoint, transformVec3AsDirection
)

# Edge Operations
###########################################

def createEdgeIndices(Py_ssize_t amount,
                      VirtualLongList indices1,
                      VirtualLongList indices2):
    cdef EdgeIndicesList edges = EdgeIndicesList(length = amount)
    cdef long index1, index2
    cdef Py_ssize_t i

    for i in range(amount):
        index1 = indices1.get(i)
        index2 = indices2.get(i)
        edges.data[i].v1 = <unsigned int>index1 if index1 >= 0 else 0
        edges.data[i].v2 = <unsigned int>index2 if index2 >= 0 else 0
    return edges

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
    ensureValidEdges(vertices, edges)

    cdef DoubleList distances = DoubleList(length = len(edges))
    cdef Py_ssize_t i
    cdef Vector3 *v1
    cdef Vector3 *v2
    for i in range(len(edges)):
        v1 = vertices.data + edges.data[i].v1
        v2 = vertices.data + edges.data[i].v2
        distances.data[i] = distanceVec3(v1, v2)
    return distances

def calculateEdgeCenters(Vector3DList vertices, EdgeIndicesList edges):
    ensureValidEdges(vertices, edges)

    cdef Vector3DList centers = Vector3DList(length = len(edges))
    cdef Py_ssize_t i
    cdef Vector3 *v1
    cdef Vector3 *v2

    for i in range(len(edges)):
        v1 = vertices.data + edges.data[i].v1
        v2 = vertices.data + edges.data[i].v2
        centers.data[i].x = (v1.x + v2.x) / 2
        centers.data[i].y = (v1.y + v2.y) / 2
        centers.data[i].z = (v1.z + v2.z) / 2

    return centers

def getEdgeStartPoints(Vector3DList vertices, EdgeIndicesList edges):
    return getEdgePoints(vertices, edges, 0)

def getEdgeEndPoints(Vector3DList vertices, EdgeIndicesList edges):
    return getEdgePoints(vertices, edges, 1)

def getEdgePoints(Vector3DList vertices, EdgeIndicesList edges, int index):
    ensureValidEdges(vertices, edges)
    assert index in (0, 1)

    cdef:
        Vector3DList points = Vector3DList(length = len(edges))
        Py_ssize_t i

    if index == 0:
        for i in range(len(points)):
            points.data[i] = vertices.data[edges.data[i].v1]
    elif index == 1:
        for i in range(len(points)):
            points.data[i] = vertices.data[edges.data[i].v2]
    return points

def ensureValidEdges(Vector3DList vertices, EdgeIndicesList edges):
    if len(edges) == 0:
        return Vector3DList()
    if edges.getMaxIndex() >= len(vertices):
        raise IndexError("Edges are invalid")


# Polygon Operations
######################################################

def polygonIndicesListFromVertexAmounts(LongList vertexAmounts):
    cdef:
        cdef long i, polyLength, currentStart
        long totalLength = vertexAmounts.getSumOfElements()
        long polygonAmount = len(vertexAmounts)
        PolygonIndicesList polygonIndices

    polygonIndices = PolygonIndicesList(
        indicesAmount = totalLength,
        polygonAmount = polygonAmount)

    for i in range(totalLength):
        polygonIndices.indices.data[i] = i

    currentStart = 0
    for i in range(polygonAmount):
        polyLength = vertexAmounts.data[i]
        if polyLength >= 3:
            polygonIndices.polyStarts.data[i] = currentStart
            polygonIndices.polyLengths.data[i] = polyLength
            currentStart += polyLength
        else:
            raise Exception("vertex amount < 3")

    return polygonIndices

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


# Get Individual Polygons Mesh
###########################################

def getIndividualPolygonsMesh(Mesh mesh):
    newVertices = getIndividualPolygons_Vertices(mesh.vertices, mesh.polygons)
    newEdges = getIndividualPolygons_Edges(mesh.polygons)
    newPolygons = getIndividualPolygons_Polygons(mesh.polygons)

    newLoopEdges = getIndividualPolygons_LoopEdges(mesh.polygons)

    newMesh = Mesh(newVertices, newEdges, newPolygons, skipValidation = True)
    newMesh.setLoopEdges(newLoopEdges)

    newMesh.transferMeshProperties(mesh,
        calcNewLoopProperty = lambda x: x.copy())

    return newMesh

def getIndividualPolygons_Vertices(Vector3DList oldVertices, PolygonIndicesList oldPolygons):
    cdef Vector3DList newVertices = Vector3DList(length = oldPolygons.indices.length)
    cdef Py_ssize_t i
    for i in range(newVertices.length):
        newVertices.data[i] = oldVertices.data[oldPolygons.indices.data[i]]
    return newVertices

def getIndividualPolygons_Edges(PolygonIndicesList oldPolygons):
    cdef EdgeIndicesList newEdges = EdgeIndicesList(length = oldPolygons.indices.length)
    cdef Py_ssize_t i, j, start, length
    for i in range(oldPolygons.getLength()):
        start = oldPolygons.polyStarts.data[i]
        length = oldPolygons.polyLengths.data[i]
        for j in range(start, start + length - 1):
            newEdges.data[j].v1 = j
            newEdges.data[j].v2 = j + 1
        newEdges.data[start + length - 1].v1 = start + length - 1
        newEdges.data[start + length - 1].v2 = start
    return newEdges

def getIndividualPolygons_Polygons(PolygonIndicesList oldPolygons):
    cdef PolygonIndicesList newPolygons = PolygonIndicesList(
        indicesAmount = oldPolygons.indices.length,
        polygonAmount = oldPolygons.getLength())

    # polyStarts is identical
    memcpy(newPolygons.polyStarts.data,
           oldPolygons.polyStarts.data,
           oldPolygons.polyStarts.length * oldPolygons.polyStarts.getElementSize())

    # polyLengths is identical
    memcpy(newPolygons.polyLengths.data,
           oldPolygons.polyLengths.data,
           oldPolygons.polyLengths.length * oldPolygons.polyLengths.getElementSize())

    cdef Py_ssize_t i
    for i in range(oldPolygons.indices.length):
        newPolygons.indices.data[i] = i

    return newPolygons

def getIndividualPolygons_LoopEdges(PolygonIndicesList oldPolygons):
    cdef UIntegerList loopEdges = UIntegerList(length = oldPolygons.indices.length)
    cdef Py_ssize_t i
    for i in range(loopEdges.length):
        loopEdges.data[i] = i
    return loopEdges


# Extract Polygon Transforms
###########################################

def extractMeshPolygonTransforms(Mesh mesh):
    centers = mesh.getPolygonCenters()
    normals = mesh.getPolygonNormals(normalized = True)
    tangents = mesh.getPolygonTangents(normalized = True)
    bitangents = mesh.getPolygonBitangents(normalized = True)
    return matricesFromNormalizedAxisData(centers, tangents, bitangents, normals)

def extractInvertedPolygonTransforms(Mesh mesh):
    centers = mesh.getPolygonCenters()
    normals = mesh.getPolygonNormals(normalized = True)
    tangents = mesh.getPolygonTangents(normalized = True)
    bitangents = mesh.getPolygonBitangents(normalized = True)
    return invertedMatricesFromNormalizedAxisData(centers, tangents, bitangents, normals)

def matricesFromNormalizedAxisData(Vector3DList origins, Vector3DList xDirections,
                                   Vector3DList yDirections, Vector3DList zDirections):
    assert origins.length == xDirections.length == yDirections.length == zDirections.length
    cdef Matrix4x4List matrices = Matrix4x4List(length = origins.length)
    cdef Py_ssize_t i
    for i in range(matrices.length):
        createMatrix(matrices.data + i, origins.data + i,
            xDirections.data + i, yDirections.data + i, zDirections.data + i)
    return matrices

def invertedMatricesFromNormalizedAxisData(Vector3DList origins, Vector3DList xDirections,
                                           Vector3DList yDirections, Vector3DList zDirections):
    assert origins.length == xDirections.length == yDirections.length == zDirections.length
    cdef Matrix4x4List matrices = Matrix4x4List(length = origins.length)
    cdef Py_ssize_t i
    for i in range(matrices.length):
        createInvertedMatrix(matrices.data + i, origins.data + i,
            xDirections.data + i, yDirections.data + i, zDirections.data + i)
    return matrices

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
cdef inline void extractPolygonData(Vector3 *vertices,
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

cdef inline void createMatrix(Matrix4 *m, Vector3 *center, Vector3 *tangent,
                              Vector3 *bitangent, Vector3 *normal):
    m.a11, m.a12, m.a13, m.a14 = tangent.x, bitangent.x, normal.x, center.x
    m.a21, m.a22, m.a23, m.a24 = tangent.y, bitangent.y, normal.y, center.y
    m.a31, m.a32, m.a33, m.a34 = tangent.z, bitangent.z, normal.z, center.z
    m.a41, m.a42, m.a43, m.a44 = 0, 0, 0, 1

cdef inline void createInvertedMatrix(Matrix4 *m, Vector3 *center, Vector3 *tangent,
                                      Vector3 *bitangent, Vector3 *normal):
    m.a11, m.a12, m.a13 = tangent.x,   tangent.y,   tangent.z,
    m.a21, m.a22, m.a23 = bitangent.x, bitangent.y, bitangent.z
    m.a31, m.a32, m.a33 = normal.x,    normal.y,    normal.z
    m.a41, m.a42, m.a43, m.a44 = 0, 0, 0, 1

    m.a14 = -(tangent.x   * center.x + tangent.y   * center.y + tangent.z   * center.z)
    m.a24 = -(bitangent.x * center.x + bitangent.y * center.y + bitangent.z * center.z)
    m.a34 = -(normal.x    * center.x + normal.y    * center.y + normal.z    * center.z)


# Edges to Tubes
###########################################

# random vector that is unlikely to be colinear to any input
cdef Vector3 upVector = {"x" : 0.5234643, "y" : 0.9871562, "z" : 0.6132743}
normalizeVec3_InPlace(&upVector)

def edgesToTubes(Vector3DList vertices, EdgeIndicesList edges, radius, Py_ssize_t resolution, bint caps = True):
    if len(edges) > 0 and edges.getMaxIndex() >= vertices.length:
        raise IndexError("invalid edges")

    cdef Mesh tube = getCylinderMesh(1, 1, resolution, caps)
    cdef VirtualDoubleList radii = VirtualDoubleList.fromListOrElement(radius, 0)
    transformations = getEdgeMatrices(vertices, edges, radii)
    return replicateMesh(tube, transformations)

def getEdgeMatrices(Vector3DList vertices, EdgeIndicesList edges, VirtualDoubleList radii):
    cdef Matrix4x4List matrices = Matrix4x4List(length = edges.length)

    cdef:
        Py_ssize_t i
        Matrix4 *m
        Vector3 *v1
        Vector3 *v2
        Vector3 xDir, yDir, zDir
        float radius, height

    for i in range(edges.length):
        v1 = vertices.data + edges.data[i].v1
        v2 = vertices.data + edges.data[i].v2
        subVec3(&zDir, v2, v1)
        crossVec3(&xDir, &zDir, &upVector)
        crossVec3(&yDir, &xDir, &zDir)
        radius = radii.get(i)
        normalizeLengthVec3_Inplace(&xDir, radius)
        normalizeLengthVec3_Inplace(&yDir, radius)

        m = matrices.data + i
        m.a11, m.a12, m.a13, m.a14 = -xDir.x, yDir.x, zDir.x, v1.x
        m.a21, m.a22, m.a23, m.a24 = -xDir.y, yDir.y, zDir.y, v1.y
        m.a31, m.a32, m.a33, m.a34 = -xDir.z, yDir.z, zDir.z, v1.z
        m.a41, m.a42, m.a43, m.a44 = 0, 0, 0, 1

    return matrices


# Replicate Mesh
###################################

def replicateMesh(Mesh source, transformations):
    cdef Py_ssize_t vertexAmount = source.vertices.length
    cdef Py_ssize_t edgeAmount = source.edges.length

    newVertices = getReplicatedVertices(source.vertices, transformations)
    newEdges = getReplicatedEdges(source.edges, len(transformations), vertexAmount)
    newPolygons = getReplicatedPolygons(source.polygons, len(transformations), vertexAmount)

    newVertexNormals = getReplicatedNormals(source.getVertexNormals(), transformations)
    newPolygonNormals = getReplicatedNormals(source.getPolygonNormals(), transformations)
    newLoopEdges = getReplicatedLoopEdges(source.getLoopEdges(), len(transformations), edgeAmount)

    mesh = Mesh(newVertices, newEdges, newPolygons, skipValidation = True)
    mesh.setVertexNormals(newVertexNormals)
    mesh.setPolygonNormals(newPolygonNormals)
    mesh.setLoopEdges(newLoopEdges)

    mesh.transferMeshProperties(source,
        calcNewLoopProperty = lambda x: x.repeated(amount = len(transformations)))

    return mesh

def getReplicatedVertices(Vector3DList oldVertices, transformations):
    if isinstance(transformations, Vector3DList):
        return getReplicatedVertices_VectorList(oldVertices, transformations)
    elif isinstance(transformations, Matrix4x4List):
        return getReplicatedVertices_MatrixList(oldVertices, transformations)

def getReplicatedVertices_VectorList(Vector3DList oldVertices, Vector3DList transformations):
    cdef Vector3DList newVertices = Vector3DList(oldVertices.length * transformations.length)
    cdef Vector3* _oldVertices = oldVertices.data
    cdef Vector3* _newVertices = newVertices.data
    cdef Vector3* _transformations = transformations.data

    cdef Py_ssize_t i, j
    cdef Py_ssize_t index = 0
    for i in range(transformations.length):
        for j in range(oldVertices.length):
            _newVertices[index].x = _oldVertices[j].x + _transformations[i].x
            _newVertices[index].y = _oldVertices[j].y + _transformations[i].y
            _newVertices[index].z = _oldVertices[j].z + _transformations[i].z
            index += 1

    return newVertices

def getReplicatedVertices_MatrixList(Vector3DList oldVertices, Matrix4x4List matrices):
    cdef Vector3DList newVertices = Vector3DList(oldVertices.length * matrices.length)
    cdef Vector3 *_newVertices = newVertices.data
    cdef Vector3 *_oldVertices = oldVertices.data
    cdef Matrix4 *_matrices = matrices.data

    cdef Py_ssize_t i, j
    cdef Py_ssize_t index = 0
    for i in range(matrices.length):
        for j in range(oldVertices.length):
            transformVec3AsPoint(_newVertices + index,
                                 _oldVertices + j,
                                 _matrices + i)
            index += 1
    return newVertices

def getReplicatedEdges(EdgeIndicesList edges, Py_ssize_t amount, Py_ssize_t vertexAmount):
    cdef Py_ssize_t edgeAmount = edges.length
    cdef EdgeIndicesList newEdges = EdgeIndicesList(length = edges.length * amount)

    cdef EdgeIndices *_oldEdges = edges.data
    cdef EdgeIndices *_newEdges = newEdges.data

    cdef Py_ssize_t i, j, offset
    cdef Py_ssize_t index = 0
    for i in range(amount):
        offset = vertexAmount * i
        for j in range(edgeAmount):
            _newEdges[index].v1 = _oldEdges[j].v1 + offset
            _newEdges[index].v2 = _oldEdges[j].v2 + offset
            index += 1
    return newEdges

def getReplicatedPolygons(PolygonIndicesList polygons, Py_ssize_t amount, Py_ssize_t vertexAmount):
    cdef Py_ssize_t indicesAmount = polygons.indices.length
    cdef Py_ssize_t polygonAmount = polygons.getLength()
    cdef PolygonIndicesList newPolygons = PolygonIndicesList(
        indicesAmount = amount * indicesAmount,
        polygonAmount = amount * polygonAmount)

    cdef unsigned int *_oldIndices = polygons.indices.data
    cdef unsigned int *_oldPolyStarts = polygons.polyStarts.data
    cdef unsigned int *_oldPolyLengths = polygons.polyLengths.data

    cdef unsigned int *_newIndices = newPolygons.indices.data
    cdef unsigned int *_newPolyStarts = newPolygons.polyStarts.data
    cdef unsigned int *_newPolyLengths = newPolygons.polyLengths.data

    cdef Py_ssize_t i, j, offset, index

    # Polygon Indices
    index = 0
    for i in range(amount):
        offset = vertexAmount * i
        for j in range(indicesAmount):
            _newIndices[index] = _oldIndices[j] + offset
            index += 1

    # Polygon Starts
    index = 0
    for i in range(amount):
        offset = indicesAmount * i
        for j in range(polygonAmount):
            _newPolyStarts[index] = _oldPolyStarts[j] + offset
            index += 1

    # Polygon Lengths
    for i in range(amount):
        memcpy(_newPolyLengths + i * polygonAmount,
               _oldPolyLengths,
               sizeof(unsigned int) * polygonAmount)

    return newPolygons

def getReplicatedNormals(Vector3DList normals, transformations):
    if isinstance(transformations, Vector3DList):
        return getReplicatedNormals_Vector3DList(normals, transformations)
    elif isinstance(transformations, Matrix4x4List):
        return getReplicatedNormals_Matrix4x4List(normals, transformations)

def getReplicatedNormals_Vector3DList(Vector3DList normals, Vector3DList transformations):
    return normals.repeated(amount = len(transformations))

def getReplicatedNormals_Matrix4x4List(Vector3DList normals, Matrix4x4List matrices):
    cdef Py_ssize_t normalsAmount = normals.length
    cdef Vector3DList newNormals = Vector3DList(length = normalsAmount * matrices.length)

    cdef Vector3 *_normals = normals.data
    cdef Vector3 *_newNormals = newNormals.data
    cdef Matrix4 *_matrices = matrices.data

    cdef Py_ssize_t i, j
    cdef Py_ssize_t index = 0
    for i in range(matrices.length):
        for j in range(normalsAmount):
            transformVec3AsDirection(
                _newNormals + index,
                _normals + j,
                _matrices + i)
            index += 1
    return newNormals

def getReplicatedLoopEdges(UIntegerList loopEdges, Py_ssize_t amount, Py_ssize_t edgeAmount):
    cdef Py_ssize_t loopEdgesAmount = loopEdges.length
    cdef UIntegerList newLoopEdges = UIntegerList(length = amount * loopEdgesAmount)

    cdef unsigned int *_loopEdges = loopEdges.data
    cdef unsigned int *_newLoopEdges = newLoopEdges.data

    cdef Py_ssize_t i, j, offset
    cdef Py_ssize_t index = 0
    for i in range(amount):
        offset = edgeAmount * i
        for j in range(loopEdgesAmount):
            _newLoopEdges[index] = _loopEdges[j] + offset
            index += 1
    return newLoopEdges
