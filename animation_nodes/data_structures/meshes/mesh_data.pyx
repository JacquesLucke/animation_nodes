# cython: profile=True
import numpy
import cython
import textwrap
import functools
from libc.math cimport sin, cos, pi
from collections import OrderedDict
from . validate import createValidEdgesList
from . validate import checkMeshData, calculateLoopEdges
from .. lists.base_lists cimport (
    UIntegerList, EdgeIndices, EdgeIndicesList, Vector3DList, Vector2DList, ColorList, LongList)
from ... math cimport (
    Vector3, crossVec3, subVec3, dotVec3, toVector3, crossVec3, lengthVec3, addVec3_Inplace,
    scaleVec3_Inplace, angleNormalizedVec3, normalizeVec3_InPlace, isExactlyZeroVec3,
    normalizeVec3, Matrix4, toMatrix4
)

def derivedMeshDataCacheHelper(name, handleNormalization = False):
    def decorator(function):
        if handleNormalization:
            @functools.wraps(function)
            def wrapper(Mesh self, normalized = False, **kwargs):
                if name not in self.derivedMeshDataCache:
                    vectors = function(self, **kwargs)
                    self.derivedMeshDataCache[name] = (vectors, False)
                vectors, isNorm = self.derivedMeshDataCache[name]
                if normalized and not isNorm:
                    vectors.normalize()
                    self.derivedMeshDataCache[name] = (vectors, True)
                return vectors
        else:
            @functools.wraps(function)
            def wrapper(Mesh self, **kwargs):
                if name not in self.derivedMeshDataCache:
                    self.derivedMeshDataCache[name] = function(self, **kwargs)
                return self.derivedMeshDataCache[name]
        return wrapper
    return decorator

cdef class Mesh:
    def __cinit__(self, Vector3DList vertices = None,
                        EdgeIndicesList edges = None,
                        PolygonIndicesList polygons = None,
                        bint skipValidation = False):

        if vertices is None: vertices = Vector3DList()
        if edges is None: edges = EdgeIndicesList()
        if polygons is None: polygons = PolygonIndicesList()

        if not skipValidation:
            checkMeshData(vertices, edges, polygons)

        self.vertices = vertices
        self.edges = edges
        self.polygons = polygons

        self.derivedMeshDataCache = {}
        self.uvMaps = OrderedDict()
        self.vertexColorLayers = OrderedDict()

    def verticesTransformed(self):
        self.derivedMeshDataCache.pop("Vertex Normals", None)
        self.derivedMeshDataCache.pop("Polygon Centers", None)
        self.derivedMeshDataCache.pop("Polygon Normals", None)
        self.derivedMeshDataCache.pop("Polygon Tangents", None)
        self.derivedMeshDataCache.pop("Polygon Bitangents", None)

    def verticesMoved(self):
        self.derivedMeshDataCache.pop("Polygon Centers", None)

    def topologyChanged(self):
        self.derivedMeshDataCache.pop("Linked Vertices", None)

    def getPolygonOrientationMatrices(self, normalized = True):
        normals = self.getPolygonNormals(normalized)
        tangents = self.getPolygonTangents(normalized)
        bitangents = self.getPolygonBitangents(normalized)
        return normals, tangents, bitangents

    @derivedMeshDataCacheHelper("Loop Edges")
    def getLoopEdges(self):
        return calculateLoopEdges(self.edges, self.polygons)

    @derivedMeshDataCacheHelper("Polygon Normals", handleNormalization = True)
    def getPolygonNormals(self):
        return calculatePolygonNormals(self.vertices, self.polygons)

    @derivedMeshDataCacheHelper("Vertex Normals", handleNormalization = True)
    def getVertexNormals(self):
        return calculateVertexNormals(self.vertices, self.polygons, self.getPolygonNormals())

    @derivedMeshDataCacheHelper("Polygon Centers")
    def getPolygonCenters(self):
        return calculatePolygonCenters(self.vertices, self.polygons)

    @derivedMeshDataCacheHelper("Polygon Tangents", handleNormalization = True)
    def getPolygonTangents(self):
        return calculatePolygonTangents(self.vertices, self.polygons)

    @derivedMeshDataCacheHelper("Polygon Bitangents", handleNormalization = True)
    def getPolygonBitangents(self):
        return calculatePolygonBitangents(self.getPolygonTangents(), self.getPolygonNormals())

    @derivedMeshDataCacheHelper("Linked Vertices")
    def getLinkedVertices(self):
        return calculateLinkedVertices(self.vertices.length, self.edges)

    def setLoopEdges(self, UIntegerList loopEdges):
        if len(loopEdges) == len(self.polygons.indices):
            self.derivedMeshDataCache["Loop Edges"] = loopEdges
        else:
            raise Exception("invalid length")

    def setPolygonNormals(self, Vector3DList normals):
        if len(normals) == len(self.polygons):
            self.derivedMeshDataCache["Polygon Normals"] = (normals, False)
        else:
            raise Exception("invalid length")

    def setVertexNormals(self, Vector3DList normals):
        if len(normals) == len(self.vertices):
            self.derivedMeshDataCache["Vertex Normals"] = (normals, False)
        else:
            raise Exception("invalid length")

    def insertUVMap(self, str name, Vector2DList uvs):
        if len(uvs) == len(self.polygons.indices):
            self.uvMaps[name] = uvs
        else:
            raise Exception("invalid length")

    def getUVMaps(self):
        return list(self.uvMaps.items())

    def getUVMapNames(self):
        return list(self.uvMaps.keys())

    def getUVMapPositions(self, str uvMapName):
        return self.uvMaps.get(uvMapName, None)

    def insertVertexColorLayer(self, str name, ColorList colors):
        if len(colors) == len(self.polygons.indices):
            self.vertexColorLayers[name] = colors
        else:
            raise Exception("invalid length")

    def getVertexColorLayers(self):
        return list(self.vertexColorLayers.items())

    def getVertexColorLayerNames(self):
        return list(self.vertexColorLayers.keys())

    def getVertexColors(self, str colorLayerName):
        return self.vertexColorLayers.get(colorLayerName, None)

    def getVertexLinkedVertices(self, long vertexIndex):
        cdef LongList neighboursAmounts, neighboursStarts, neighbours, neighbourEdges
        neighboursAmounts, neighboursStarts, neighbours, neighbourEdges = self.getLinkedVertices()

        cdef int start, end, amount
        amount = neighboursAmounts.data[vertexIndex]
        start = neighboursStarts.data[vertexIndex]
        end = start + amount

        return neighbours[start:end], neighbourEdges[start:end], amount

    def copy(self):
        mesh = Mesh(self.vertices.copy(), self.edges.copy(), self.polygons.copy())
        mesh.transferMeshProperties(self,
            calcNewLoopProperty = lambda x: x.copy())
        return mesh

    def transform(self, transformation):
        self.vertices.transform(transformation)
        self.verticesTransformed()

    def move(self, translation):
        self.vertices.move(translation)
        self.verticesMoved()

    def triangulateMesh(self, str method = "FAN"):
        polygons = self.polygons
        if method == "FAN":
            newPolygons = triangulatePolygonsUsingFanSpanMethod(polygons)
        elif method == "EAR":
            newPolygons = triangulatePolygonsUsingEarClipMethod(self.vertices, polygons)
        self.edges = createValidEdgesList(polygons = newPolygons)
        self.polygons = newPolygons

    def __repr__(self):
        return textwrap.dedent(
        f"""AN Mesh Object:
        Vertices: {len(self.vertices)}
        Edges: {len(self.edges)}
        Polygons: {len(self.polygons)}
        UV Maps: {self.getUVMapNames()}
        Vertex Colors: {self.getVertexColorLayerNames()}""")

    def transferMeshProperties(self, Mesh source, *, calcNewLoopProperty = None):
        if calcNewLoopProperty is not None:
            for name, uvMap in source.uvMaps.items():
                self.uvMaps[name] = calcNewLoopProperty(uvMap)

            for name, vertexColorLayer in source.vertexColorLayers.items():
                self.vertexColorLayers[name] = calcNewLoopProperty(vertexColorLayer)

    @classmethod
    def join(cls, *meshes):
        cdef Mesh newMesh = Mesh()
        for meshData in meshes:
            newMesh.append(meshData)
        return newMesh

    def append(self, Mesh meshData):
        cdef long vertexOffset = self.vertices.length
        cdef long edgeOffset = self.edges.length
        cdef long polygonIndicesOffset = self.polygons.indices.length
        cdef long i

        self.vertices.extend(meshData.vertices)

        self.edges.extend(meshData.edges)
        for i in range(meshData.edges.length):
            self.edges.data[edgeOffset + i].v1 += vertexOffset
            self.edges.data[edgeOffset + i].v2 += vertexOffset

        self.polygons.extend(meshData.polygons)
        for i in range(meshData.polygons.indices.length):
            self.polygons.indices.data[polygonIndicesOffset + i] += vertexOffset


def calculatePolygonNormals(Vector3DList vertices, PolygonIndicesList polygons):
    cdef Vector3DList normals = Vector3DList(length = polygons.getLength())
    cdef Vector3 *_normals = normals.data

    cdef Vector3 *_vertices = vertices.data

    cdef unsigned int *indices = polygons.indices.data
    cdef unsigned int *polyStarts = polygons.polyStarts.data
    cdef unsigned int *polyLengths = polygons.polyLengths.data
    cdef unsigned int start, length

    cdef Py_ssize_t i
    cdef Vector3 dirA, dirB
    for i in range(polygons.getLength()):
        start = polyStarts[i]
        length = polyLengths[i]

        subVec3(&dirA, _vertices + indices[start + 1], _vertices + indices[start])
        subVec3(&dirB, _vertices + indices[start + length - 1], _vertices + indices[start])
        crossVec3(_normals + i, &dirA, &dirB)

    return normals


def calculateVertexNormals(Vector3DList vertices, PolygonIndicesList polygons, Vector3DList polygonNormals):
    cdef Vector3DList vertexNormals = Vector3DList(length = vertices.length)
    cdef Vector3 *_vertexNormals = vertexNormals.data
    vertexNormals.fill(0)

    cdef Vector3 *_polygonNormals = polygonNormals.data

    cdef unsigned int *indices = polygons.indices.data
    cdef unsigned int *polyStarts = polygons.polyStarts.data
    cdef unsigned int *polyLengths = polygons.polyLengths.data
    cdef unsigned int start, length

    cdef Py_ssize_t i,j
    cdef Vector3 normalizedNormal
    for i in range(polygons.getLength()):
        start = polyStarts[i]
        length = polyLengths[i]
        normalizeVec3(&normalizedNormal, _polygonNormals + i)

        for j in range(start, start + length):
            # can be improved by weighting by angle
            addVec3_Inplace(_vertexNormals + indices[j], &normalizedNormal)

    for i in range(vertices.length):
        if isExactlyZeroVec3(_vertexNormals + i):
            # default: vertex location as normal
            _vertexNormals[i] = vertices.data[i]

    return vertexNormals


def calculatePolygonCenters(Vector3DList vertices, PolygonIndicesList polygons):
    cdef Vector3DList centers = Vector3DList(length = polygons.getLength())
    centers.fill(0)

    cdef Vector3 *_centers = centers.data
    cdef Vector3 *_vertices = vertices.data

    cdef unsigned int *indices = polygons.indices.data
    cdef unsigned int *polyStarts = polygons.polyStarts.data
    cdef unsigned int *polyLengths = polygons.polyLengths.data
    cdef unsigned int start, length

    cdef Py_ssize_t i, j
    for i in range(polygons.getLength()):
        start = polyStarts[i]
        length = polyLengths[i]

        for j in range(start, start + length):
            _centers[i].x += _vertices[indices[j]].x
            _centers[i].y += _vertices[indices[j]].y
            _centers[i].z += _vertices[indices[j]].z

        _centers[i].x /= length
        _centers[i].y /= length
        _centers[i].z /= length

    return centers

def calculatePolygonTangents(Vector3DList vertices, PolygonIndicesList polygons):
    cdef Vector3DList tangents = Vector3DList(length = polygons.getLength())

    cdef Vector3 *_tangents = tangents.data
    cdef Vector3 *_vertices = vertices.data

    cdef unsigned int *indices = polygons.indices.data
    cdef unsigned int *polyStarts = polygons.polyStarts.data
    cdef unsigned int *polyLengths = polygons.polyLengths.data
    cdef unsigned int start, length

    cdef Py_ssize_t i, indexA, indexB
    for i in range(polygons.getLength()):
        start = polyStarts[i]
        indexA = indices[start + 0]
        indexB = indices[start + 1]
        _tangents[i].x = _vertices[indexB].x - _vertices[indexA].x
        _tangents[i].y = _vertices[indexB].y - _vertices[indexA].y
        _tangents[i].z = _vertices[indexB].z - _vertices[indexA].z

    return tangents

def calculatePolygonBitangents(Vector3DList tangents, Vector3DList normals):
    return calculateCrossProducts(tangents, normals)

def calculateCrossProducts(Vector3DList a, Vector3DList b):
    cdef Vector3DList result = Vector3DList(length = a.length)
    cdef Py_ssize_t i

    cdef Vector3 *_result = result.data
    cdef Vector3 *_a = a.data
    cdef Vector3 *_b = b.data

    for i in range(len(result)):
        crossVec3(_result + i, _a + i, _b + i)

    return result

def calculateLinkedVertices(int verticesAmount, EdgeIndicesList edges):
    cdef int i, j
    cdef int edgesAmount = edges.length

    # Compute how many neighbours each vertex have.
    cdef LongList neighboursAmounts = LongList.fromValue(0, length = verticesAmount)
    for i in range(edgesAmount):
        neighboursAmounts.data[edges.data[i].v1] += 1
        neighboursAmounts.data[edges.data[i].v2] += 1

    # Compute the start index of each group of neighbours of each vertex.
    cdef LongList neighboursStarts = LongList(length = verticesAmount)
    cdef int start = 0
    for i in range(verticesAmount):
        neighboursStarts.data[i] = start
        start += neighboursAmounts.data[i]

    # Keep track of how many indices are there in each group of neighbours at each iteration.
    cdef LongList usedSlots = LongList.fromValue(0, length = verticesAmount)

    # Compute the indices of neighbouring vertices and edges of each vertex.
    cdef unsigned int v1, v2
    cdef LongList neighbours = LongList(length = edgesAmount * 2)
    cdef LongList neighbourEdges = LongList(length = edgesAmount * 2)
    for i in range(edgesAmount):
        v1, v2 = edges.data[i].v1, edges.data[i].v2
        neighbours.data[neighboursStarts.data[v1] + usedSlots.data[v1]] = v2
        neighbours.data[neighboursStarts.data[v2] + usedSlots.data[v2]] = v1
        neighbourEdges.data[neighboursStarts.data[v1] + usedSlots.data[v1]] = i
        neighbourEdges.data[neighboursStarts.data[v2] + usedSlots.data[v2]] = i
        usedSlots.data[v1] += 1
        usedSlots.data[v2] += 1

    return neighboursAmounts, neighboursStarts, neighbours, neighbourEdges

def triangulatePolygonsUsingFanSpanMethod(PolygonIndicesList polygons):
    cdef unsigned int *_oldPolyLengths = polygons.polyLengths.data
    cdef Py_ssize_t polygonAmount = polygons.getLength()
    cdef Py_ssize_t i, triAmount, polyLength

    triAmount = 0
    for i in range(polygonAmount):
        polyLength = _oldPolyLengths[i]
        if polyLength > 3:
            triAmount += polyLength - 2
        else:
            triAmount += 1

    cdef unsigned int *_oldIndices = polygons.indices.data
    cdef unsigned int *_oldPolyStarts = polygons.polyStarts.data

    cdef PolygonIndicesList newPolygons = PolygonIndicesList(
                                          indicesAmount = 3 * triAmount,
                                          polygonAmount = triAmount)
    cdef unsigned int *_newIndices = newPolygons.indices.data
    cdef unsigned int *_newPolyStarts = newPolygons.polyStarts.data
    cdef unsigned int *_newPolyLengths = newPolygons.polyLengths.data

    cdef Py_ssize_t j, index, triIndex, start

    index = 0
    triIndex = 0
    for i in range(polygonAmount):
        start = _oldPolyStarts[i]
        for j in range(_oldPolyLengths[i] - 2):
            _newPolyStarts[triIndex] = index
            _newPolyLengths[triIndex] = 3
            triIndex += 1

            _newIndices[index] = _oldIndices[start]
            _newIndices[index + 1] = _oldIndices[start + 1 + j]
            _newIndices[index + 2] = _oldIndices[start + 2 + j]
            index += 3

    return newPolygons

@cython.cdivision(True)
def triangulatePolygonsUsingEarClipMethod(Vector3DList oldVertices, PolygonIndicesList polygons):
    cdef unsigned int *_oldPolyLengths = polygons.polyLengths.data
    cdef Py_ssize_t polygonAmount = polygons.getLength()
    cdef Py_ssize_t i, triAmount, polyLength

    # Total number of triangle polygons
    triAmount = 0
    for i in range(polygonAmount):
        polyLength = _oldPolyLengths[i]
        if polyLength > 3:
            triAmount += polyLength - 2
        else:
            triAmount += 1

    cdef unsigned int *_oldIndices = polygons.indices.data
    cdef unsigned int *_oldPolyStarts = polygons.polyStarts.data

    cdef PolygonIndicesList newPolygons = PolygonIndicesList(
                                          indicesAmount = 3 * triAmount,
                                          polygonAmount = triAmount)
    cdef unsigned int *_newIndices = newPolygons.indices.data
    cdef unsigned int *_newPolyStarts = newPolygons.polyStarts.data
    cdef unsigned int *_newPolyLengths = newPolygons.polyLengths.data

    cdef Vector3 preVertex, earVertex, nexVertex, ab, bc, v1, v2, v3
    cdef LongList neighbors, indices, angles, sortAngles
    cdef Vector3DList polyVertices
    cdef float angle
    cdef Py_ssize_t polyStart, triIndex, polyIndex
    cdef Py_ssize_t j, k, amount, index, preIndex, earIndex, nexIndex

    triIndex = 0
    polyIndex = 0
    for i in range(polygonAmount):
        polyLength = _oldPolyLengths[i]
        polyStart = _oldPolyStarts[i]
        neighbors = LongList(length = polyLength)
        indices = LongList(length = polyLength)
        for j in range(polyLength):
            neighbors.data[j] = _oldIndices[polyStart + j]
            indices.data[j] = j

        polyVertices = transformVerticesOfPolygon(oldVertices, neighbors)
        if not polyCounterClockwise(polyVertices):
            neighbors = neighbors.reversed()
            polyVertices = polyVertices.reversed()

        for j in range(polyLength):
            amount = indices.length

            if amount == 3:
                _newPolyStarts[triIndex] = polyIndex
                _newPolyLengths[triIndex] = 3
                triIndex += 1

                _newIndices[polyIndex] = neighbors.data[indices.data[0]]
                _newIndices[polyIndex + 1] = neighbors.data[indices.data[1]]
                _newIndices[polyIndex + 2] = neighbors.data[indices.data[2]]
                polyIndex += 3

                break

            # Calculate inner-angle for all vertices of polygon
            angles = LongList(length = amount)
            for k in range(amount):
                preVertex = polyVertices.data[indices.data[(amount + k - 1) % amount]]
                earVertex = polyVertices.data[indices.data[k]]
                nexVertex = polyVertices.data[indices.data[(k + 1) % amount]]

                subVec3(&ab, &earVertex, &preVertex)
                subVec3(&bc, &earVertex, &nexVertex)

                normalizeVec3_InPlace(&ab)
                normalizeVec3_InPlace(&bc)

                angle = angleNormalizedVec3(&ab, &bc)
                angles.data[k] = int((angle - angle % 0.001) * 180.0 / pi)
            sortAngles = LongList.fromNumpyArray(numpy.sort(angles.asMemoryView()).astype(int))

            # Removing an ear which has smallest inner-angle
            for k in range(amount):
                index = angles.index(sortAngles[k])
                preIndex = indices.data[(amount + index - 1) % amount]
                earIndex = indices.data[index]
                nexIndex = indices.data[(index + 1) % amount]

                v1 = polyVertices.data[preIndex]
                v2 = polyVertices.data[earIndex]
                v3 = polyVertices.data[nexIndex]
                if convexVertex(v1, v2, v3) and not pointsInTriangle(polyVertices, v1, v2, v3, preIndex, earIndex, nexIndex):
                    indices = LongList.fromNumpyArray(numpy.delete(indices.asMemoryView(), index).astype(int))

                    _newPolyStarts[triIndex] = polyIndex
                    _newPolyLengths[triIndex] = 3
                    triIndex += 1

                    _newIndices[polyIndex] = neighbors.data[preIndex]
                    _newIndices[polyIndex + 1] = neighbors.data[earIndex]
                    _newIndices[polyIndex + 2] = neighbors.data[nexIndex]
                    polyIndex += 3

                    break

    return newPolygons

# Make sure normal (+z) are correct.
@cython.cdivision(True)
cdef polyCounterClockwise(Vector3DList vertices):
    cdef Py_ssize_t amount = vertices.length
    cdef float area = 0
    cdef Vector3 v1, v2
    cdef Py_ssize_t i

    for i in range(amount):
        v1 = vertices.data[i]
        v2 = vertices.data[(i + 1) % amount]
        area += (v2.x - v1.x) * (v2.y + v1.y)
    if area > 0: return False
    return True

# Make sure normal (+z) are correct, and polygon is counter clockwise.
cdef convexVertex(Vector3 v1, Vector3 v2, Vector3 v3):
    cdef float sign = (v2.x - v1.x) * (v3.y - v1.y) - (v2.y - v1.y) * (v3.x - v1.x)
    if sign >= 0: return True
    return False

# Checking points (reflex type) lies in the new triangle
cdef pointsInTriangle(Vector3DList vertices, Vector3 v1, Vector3 v2, Vector3 v3,
                      Py_ssize_t preIndex, Py_ssize_t earIndex, Py_ssize_t nexIndex):
    cdef Py_ssize_t i
    for i in range(vertices.length):
        if i != preIndex and i != earIndex and i != nexIndex and pointInsideTriangle(v1, v2, v3, vertices.data[i]):
            return True
    return False

@cython.cdivision(True)
cdef pointInsideTriangle(Vector3 v1, Vector3 v2, Vector3 v3, Vector3 p):
    cdef Vector3 u, v, w, n
    subVec3(&u, &v2, &v1)
    subVec3(&v, &v3, &v1)
    subVec3(&w, &p, &v1)

    cdef float delta = 0.00001
    v.x += delta
    v.y += delta
    v.z += delta

    crossVec3(&n, &u, &v)
    cdef float normSq = lengthVec3(&n)
    normSq = normSq * normSq

    cdef Vector3 uw, wv
    crossVec3(&uw, &u, &w)
    crossVec3(&wv, &w, &v)

    cdef float alpha = dotVec3(&uw, &n) / normSq
    cdef float beta = dotVec3(&wv, &n) / normSq
    cdef float gamma = 1 - alpha - beta
    if alpha >= 0 and alpha <= 1 and beta >= 0 and beta <= 1 and gamma >= 0 and gamma <= 1:
        return True
    else:
        return False

# Transformation of vertices of polygon into xy-plane
@cython.cdivision(True)
cdef transformVerticesOfPolygon(Vector3DList vertices, LongList polygonIndices):
    cdef Py_ssize_t polyLength = polygonIndices.length
    cdef Vector3DList polyVertices = Vector3DList(length = polyLength)

    # Compute polygon normal with Nowell's method
    cdef Vector3 polyNormal = toVector3((0, 0, 0))
    cdef Py_ssize_t i
    for i in range(polyLength):
        v1 = vertices.data[polygonIndices.data[i]]
        v2 = vertices.data[polygonIndices.data[(i + 1) % polyLength]]

        polyNormal.x += (v1.y - v2.y) * (v1.z + v2.z)
        polyNormal.y += (v1.z - v2.z) * (v1.x + v2.x)
        polyNormal.z += (v1.x - v2.x) * (v1.y + v2.y)

        polyVertices.data[i] = v1
    normalizeVec3_InPlace(&polyNormal)

    # Calculate the coefficient for Rodrigues's rotation formula
    cdef Vector3 zAxis = toVector3((0, 0, 1))
    cdef Vector3 rotAxis
    crossVec3(&rotAxis, &polyNormal, &zAxis)
    normalizeVec3_InPlace(&rotAxis)

    cdef float angle = angleNormalizedVec3(&polyNormal, &zAxis)
    cdef float sint = sin(angle)
    cdef float cost = cos(angle)
    cdef float fact = 1 - cost

    # Rotating vertices of polygon, and droping the z-comp
    cdef Vector3DList rotPolyVertices = Vector3DList(length = polyLength)
    cdef Vector3 vertex, cross, rotPolyVertex
    cdef float dot
    for i in range(polyLength):
        vertex = polyVertices.data[i]
        crossVec3(&cross, &rotAxis, &vertex)
        dot = dotVec3(&rotAxis, &vertex)

        rotPolyVertex.x = cost * vertex.x + sint * cross.x + dot * fact * rotAxis.x
        rotPolyVertex.y = cost * vertex.y + sint * cross.y + dot * fact * rotAxis.y
        rotPolyVertex.z = cost * vertex.z + sint * cross.z + dot * fact * rotAxis.z
        rotPolyVertices.data[i].x = rotPolyVertex.x
        rotPolyVertices.data[i].y = rotPolyVertex.y
        rotPolyVertices.data[i].z = 0

    # Compute avg. vector
    cdef Vector3 avgVector = toVector3((0, 0, 0))
    for i in range(polyLength):
        avgVector.x += rotPolyVertices.data[i].x
        avgVector.y += rotPolyVertices.data[i].y
        avgVector.z += rotPolyVertices.data[i].z
    scaleVec3_Inplace(&avgVector, 1.0 / polyLength)

    # Bring vertices of polygon to the world center
    cdef Vector3DList offsetPolyVertices = Vector3DList(length = polyLength)
    for i in range(polyLength):
        offsetPolyVertices.data[i].x =  rotPolyVertices.data[i].x - avgVector.x
        offsetPolyVertices.data[i].y =  rotPolyVertices.data[i].y - avgVector.y
        offsetPolyVertices.data[i].z =  rotPolyVertices.data[i].z - avgVector.z

    return offsetPolyVertices
