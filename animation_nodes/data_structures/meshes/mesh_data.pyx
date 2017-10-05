# cython: profile=True
from libc.stdint cimport uint32_t
from cpython.ref cimport PyObject
from collections import namedtuple
import functools
from .. lists.base_lists cimport UIntegerList, EdgeIndices, IntegerList, Vector3DList
from ... math cimport Vector3, crossVec3, subVec3, addVec3_Inplace, isExactlyZeroVec3, normalizeVec3

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
        self.vertexProperties = {}
        self.edgeProperties = {}
        self.polygonProperties = {}
        self.loopProperties = {}

    def verticesChanged(self):
        self.derivedMeshDataCache.pop("Vertex Normals", None)
        self.derivedMeshDataCache.pop("Polygon Centers", None)
        self.derivedMeshDataCache.pop("Polygon Normals", None)
        self.derivedMeshDataCache.pop("Polygon Tangents", None)
        self.derivedMeshDataCache.pop("Polygon Bitangents", None)

    @derivedMeshDataCacheHelper("Loop Edges")
    def getLoopEdges(self):
        return calculateLoopEdges(self.edges, self.polygons)

    @derivedMeshDataCacheHelper("Polygon Normals", handleNormalization = True)
    def getPolygonNormals(self):
        return calculatePolygonNormals(self.vertices, self.polygons)

    @derivedMeshDataCacheHelper("Vertex Normals", handleNormalization = True)
    def getVertexNormals(self, normalized = False):
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

    def setLoopEdges(self, UIntegerList loopEdges):
        if len(loopEdges) == len(self.polygons.indices):
            self.derivedMeshDataCache["Loop Edges"] = loopEdges
        else:
            raise Exception("invalid length")

    def setPolygonNormals(self, Vector3DList normals):
        if len(normals) == len(self.polygons):
            self.derivedMeshDataCache["Polygon Normals"] = normals
        else:
            raise Exception("invalid length")

    def setVertexNormals(self, Vector3DList normals):
        if len(normals) == len(self.vertices):
            self.derivedMeshDataCache["Vertex Normals"] = normals
        else:
            raise Exception("invalid length")

    def copy(self):
        return Mesh(self.vertices.copy(), self.edges.copy(), self.polygons.copy())

    def __repr__(self):
        return "<AN Mesh Object: Vertices: {}, Edges: {}, Polygons: {}>".format(
                len(self.vertices), len(self.edges), len(self.polygons))

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


def checkMeshData(Vector3DList vertices, EdgeIndicesList edges, PolygonIndicesList polygons):
    if edges.length > 0 and edges.getMaxIndex() >= vertices.length:
        raise Exception("there is an edge that references a not existing vertex")
    if polygons.getLength() > 0 and polygons.getMaxIndex() >= vertices.length:
        raise Exception("there is a polygon that references a not existing vertex")

    checkIndividualEdgeVadility(edges)
    checkIndividualPolygonValidity(polygons)

    cdef UIntegerList edgeHashes = getEdgeHashes(edges)
    cdef UIntegerList polygonHashes = getPolygonHashes(polygons)

    cdef IntegerList edgesDict = getDictForEdgeHashes(edgeHashes, edges, ignoreDuplicates = False)
    cdef IntegerList polygonsDict = getDictForPolygonHashes(polygonHashes, polygons)

    checkIfAllRequiredEdgesExist(polygons, edges, edgeHashes, edgesDict)

def checkIfAllRequiredEdgesExist(PolygonIndicesList polygons, EdgeIndicesList edges,
                                 UIntegerList edgeHashes, IntegerList edgesDict):
    cdef unsigned int *indices = polygons.indices.data
    cdef unsigned int *polyStarts = polygons.polyStarts.data
    cdef unsigned int *polyLengths = polygons.polyLengths.data
    cdef unsigned int start, length

    cdef unsigned int mask = edgesDict.length - 1

    cdef Py_ssize_t i, j
    for i in range(polygons.getLength()):
        start = polyStarts[i]
        length = polyLengths[i]

        for j in range(start, start + length - 1):
            if not edgeExistsInDict(indices[j], indices[j+1], edges.data, edgesDict.data, mask):
                raise Exception("an edge is not available for polygon {}".format(i))

        if not edgeExistsInDict(indices[start], indices[start + length - 1], edges.data, edgesDict.data, mask):
            raise Exception("an edge is not available for polygon {}".format(i))

def calculateLoopEdges(EdgeIndicesList edges, PolygonIndicesList polygons):
    cdef UIntegerList edgeHashes = getEdgeHashes(edges)
    cdef IntegerList edgesDict = getDictForEdgeHashes(edgeHashes, edges)

    cdef UIntegerList result = UIntegerList(length = polygons.indices.length)

    cdef unsigned int *indices = polygons.indices.data
    cdef unsigned int *polyStarts = polygons.polyStarts.data
    cdef unsigned int *polyLengths = polygons.polyLengths.data
    cdef unsigned int start, length
    cdef unsigned int mask = edgesDict.length - 1

    cdef Py_ssize_t i, j
    for i in range(polygons.getLength()):
        start = polyStarts[i]
        length = polyLengths[i]

        for j in range(start, start + length - 1):
            result.data[j] = getEdgeIndex(indices[j], indices[j+1], edges.data, edgesDict.data, mask)

        result.data[start+length-1] = getEdgeIndex(indices[start], indices[start + length - 1], edges.data, edgesDict.data, mask)

    return result

cdef inline char edgeExistsInDict(unsigned int i1, unsigned int i2,
                                  EdgeIndices *edges, int *edgesDict,
                                  unsigned int mask):
    return getEdgeIndex(i1, i2, edges, edgesDict, mask) >= 0

cdef inline Py_ssize_t getEdgeIndex(unsigned int i1, unsigned int i2,
                                      EdgeIndices *edges, int *edgesDict,
                                      unsigned int mask):
    cdef unsigned int slot = (hashUInt(i1) ^ hashUInt(i2)) & mask
    cdef int index
    while True:
        index = edgesDict[slot]
        if index < 0:
            return -1
        if (edges[index].v1 == i1 and edges[index].v2 == i2) or (edges[index].v1 == i2 and edges[index].v2 == i1):
            return index
        slot = (slot + 1) & mask



def checkIndividualEdgeVadility(EdgeIndicesList edges):
    cdef Py_ssize_t i
    cdef EdgeIndices *_edges = edges.data
    for i in range(edges.length):
        if _edges[i].v1 == _edges[i].v2:
            raise Exception("Vertex cannot be connected to itself (index: {}, value: {})"
                            .format(i, edges[i]))

def checkIndividualPolygonValidity(PolygonIndicesList polygons):
    cdef unsigned int *indices = polygons.indices.data
    cdef unsigned int *polyStarts = polygons.polyStarts.data
    cdef unsigned int *polyLengths = polygons.polyLengths.data
    cdef unsigned int start, length
    cdef bint invalid

    cdef Py_ssize_t i, j, k
    for i in range(polygons.getLength()):
        start = polyStarts[i]
        length = polyLengths[i]

        if length == 3:
            invalid = (indices[start+0] == indices[start+1]
                    or indices[start+0] == indices[start+2]
                    or indices[start+1] == indices[start+2])
        elif length == 4:
            invalid = (indices[start+0] == indices[start+1]
                    or indices[start+0] == indices[start+2]
                    or indices[start+0] == indices[start+3]
                    or indices[start+1] == indices[start+2]
                    or indices[start+1] == indices[start+3]
                    or indices[start+2] == indices[start+3])
        else:
            invalid = False
            for j in range(start, start + length - 1):
                for k in range(start + j + 1, start + length):
                    invalid = invalid or (indices[j] == indices[k])

        if invalid:
            raise Exception("Polygon cannot use a Vertex twice (index: {}, value: {})"
                            .format(i, polygons[i]))


def getEdgeHashes(EdgeIndicesList edges):
    cdef UIntegerList hashes = UIntegerList(length = edges.length)
    cdef unsigned int *_hashes = hashes.data
    cdef EdgeIndices *_edges = edges.data
    cdef Py_ssize_t i
    for i in range(edges.length):
        _hashes[i] = hashUInt(_edges[i].v1) ^ hashUInt(_edges[i].v2)
    return hashes

def getPolygonHashes(PolygonIndicesList polygons):
    cdef UIntegerList hashes = UIntegerList(length = polygons.getLength())
    cdef unsigned int *_hashes = hashes.data

    cdef unsigned int *indices = polygons.indices.data
    cdef unsigned int *polyStarts = polygons.polyStarts.data
    cdef unsigned int *polyLengths = polygons.polyLengths.data
    cdef unsigned int start, length

    cdef Py_ssize_t i, j
    for i in range(polygons.getLength()):
        start = polyStarts[i]
        length = polyLengths[i]
        if length == 3:
            _hashes[i] = hashUInt(indices[start]) ^ hashUInt(indices[start+1]) ^ hashUInt(indices[start+2])
        elif length == 4:
            _hashes[i] = hashUInt(indices[start]) ^ hashUInt(indices[start+1]) ^ hashUInt(indices[start+2]) ^ hashUInt(indices[start+3])
        else:
            _hashes[i] = 0
            for j in range(start, start + length):
                _hashes[i] ^= hashUInt(indices[j])

    return hashes

cdef inline uint32_t hashUInt(uint32_t x):
    x = ((x >> 16) ^ x) * 0x45d9f3b
    x = ((x >> 16) ^ x) * 0x45d9f3b
    x = (x >> 16) ^ x
    return x


ctypedef char (*HandleDuplicateFunction)(void *settings, unsigned int i1, unsigned int i2)

def getDictForPolygonHashes(UIntegerList hashes, PolygonIndicesList polygons):
    cdef PolygonListData data
    data.indices = polygons.indices.data
    data.polyStarts = polygons.polyStarts.data
    data.polyLengths = polygons.polyLengths.data
    return createDictForHashes(hashes, comparePolygons, &data)

cdef struct PolygonListData:
    unsigned int *indices
    unsigned int *polyStarts
    unsigned int *polyLengths

def getDictForEdgeHashes(UIntegerList hashes, EdgeIndicesList edges, bint ignoreDuplicates = False):
    if ignoreDuplicates:
        return createDictForHashes(hashes, compareEdges_IgnoreDuplicate, edges.data)
    else:
        return createDictForHashes(hashes, compareEdges_FailOnDuplicate, edges.data)

cdef char compareEdges_FailOnDuplicate(void *settings, unsigned int i1, unsigned int i2):
    return 2 if areEdgesEqual(settings, i1, i2) else 0

cdef char compareEdges_IgnoreDuplicate(void *settings, unsigned int i1, unsigned int i2):
    return 1 if areEdgesEqual(settings, i1, i2) else 0

cdef inline char areEdgesEqual(void *settings, unsigned int i1, unsigned int i2):
    cdef EdgeIndices *edges = <EdgeIndices*>settings
    return ((edges[i1].v1 == edges[i2].v1 and edges[i1].v2 == edges[i2].v2)
         or (edges[i1].v1 == edges[i2].v2 and edges[i1].v2 == edges[i2].v1))


cdef char comparePolygons(void *settings, unsigned int i1, unsigned int i2):
    cdef PolygonListData *data = <PolygonListData*>settings
    cdef unsigned int *indices = data.indices
    cdef unsigned int *polyStarts = data.polyStarts
    cdef unsigned int *polyLengths = data.polyLengths

    # First compare lengths
    cdef unsigned int length1 = polyLengths[i1]
    cdef unsigned int length2 = polyLengths[i2]
    if length1 != length2:
        return 0
    cdef unsigned int length = length1

    # Then calculate a simple hash using a commutative operations
    # this way we don't have to sort the indices most of the time
    cdef unsigned int s1 = polyStarts[i1]
    cdef unsigned int s2 = polyStarts[i2]
    cdef unsigned int sum1, sum2
    cdef Py_ssize_t i

    if length == 3:
        sum1 = indices[s1+0] + indices[s1+1] + indices[s1+2]
        sum2 = indices[s2+0] + indices[s2+1] + indices[s2+2]
    elif length == 4:
        sum1 = indices[s1+0] + indices[s1+1] + indices[s1+2] + indices[s1+3]
        sum2 = indices[s2+0] + indices[s2+1] + indices[s2+2] + indices[s2+3]
    else:
        sum1 = sum2 = 0
        for i in range(s1, s1 + length):
            sum1 += indices[i]
        for i in range(s2, s2 + length):
            sum2 += indices[i]

    # do real comparison if length and sum are equal
    if sum1 == sum2:
        p1 = [indices[i] for i in range(s1, s1 + length)]
        p2 = [indices[i] for i in range(s2, s2 + length)]
        if set(p1) == set(p2):
            return 2

    return 0

cdef createDictForHashes(UIntegerList hashes, HandleDuplicateFunction handleDuplicate, void *settings):
    cdef Py_ssize_t maskSize = max(hashes.length-1, 0).bit_length() + 1
    cdef Py_ssize_t indexSize = 2 ** maskSize
    cdef unsigned int mask = indexSize - 1 # produces something like ...00011111

    cdef IntegerList fullDict = IntegerList.fromValue(-1, length = indexSize)
    cdef int *_fullDict = fullDict.data


    cdef Py_ssize_t i, indexInSlot
    cdef unsigned int slot, currentHash
    cdef char duplicateType

    for i in range(hashes.length):
        currentHash = hashes.data[i]

        slot = currentHash & mask
        indexInSlot = _fullDict[slot]

        while indexInSlot >= 0:
            if currentHash == hashes.data[indexInSlot]:
                duplicateType = handleDuplicate(settings, i, indexInSlot)
                if duplicateType == 0:
                    pass # no real duplicate, just same hashes
                if duplicateType == 1:
                    break # ignore duplicate
                elif duplicateType == 2:
                    raise Exception("duplicates at {} and {}".format(i, indexInSlot))

            slot = (slot + 1) & mask
            indexInSlot = _fullDict[slot]

        _fullDict[slot] = i


    return fullDict


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


def createValidEdgesList(EdgeIndicesList edges, PolygonIndicesList polygons):
    cdef EdgeIndicesList allEdges = edges + getAllPolygonEdges(polygons)
    cdef UIntegerList edgeHashes = getEdgeHashes(allEdges)
    cdef IntegerList edgesDict = getDictForEdgeHashes(edgeHashes, allEdges, ignoreDuplicates = True)

    cdef EdgeIndicesList newEdges = EdgeIndicesList(capacity = allEdges.length)
    cdef Py_ssize_t index = 0
    cdef Py_ssize_t i
    for i in range(edgesDict.length):
        if edgesDict.data[i] >= 0:
            newEdges.data[index] = allEdges.data[edgesDict.data[i]]
            index += 1
    newEdges.length = index
    newEdges.shrinkToLength()
    return newEdges

def getAllPolygonEdges(PolygonIndicesList polygons):
    cdef EdgeIndicesList edges = EdgeIndicesList(length = polygons.indices.length)

    cdef unsigned int *indices = polygons.indices.data
    cdef unsigned int *polyStarts = polygons.polyStarts.data
    cdef unsigned int *polyLengths = polygons.polyLengths.data
    cdef unsigned int start, length

    cdef Py_ssize_t i, j
    cdef Py_ssize_t index = 0
    for i in range(polygons.getLength()):
        start = polyStarts[i]
        length = polyLengths[i]

        for j in range(start, start + length - 1):
            edges.data[index].v1 = indices[j]
            edges.data[index].v2 = indices[j+1]
            index += 1

        edges.data[index].v1 = indices[start]
        edges.data[index].v2 = indices[start + length - 1]
        index += 1

    return edges

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
    cdef Vector3DList bitangents = Vector3DList(length = tangents.length)
    cdef Py_ssize_t i
    for i in range(bitangents.length):
        crossVec3(bitangents.data + i, tangents.data + i, normals.data + i)
    return bitangents
