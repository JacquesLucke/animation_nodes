# cython: profile=True
import textwrap
import functools
from collections import OrderedDict
from . validate import checkMeshData, calculateLoopEdges
from .. lists.base_lists cimport UIntegerList, EdgeIndices, Vector3DList, Vector2DList
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
        self.uvMaps = OrderedDict()

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

    def copy(self):
        mesh = Mesh(self.vertices.copy(), self.edges.copy(), self.polygons.copy())
        mesh.transferMeshProperties(self,
            calcNewLoopProperty = lambda x: x.copy())
        return mesh

    def __repr__(self):
        return textwrap.dedent("""\
            AN Mesh Object:
                Vertices: {}
                Edges: {}
                Polygons: {}
                UV Maps: {}\
            """.format(len(self.vertices), len(self.edges), len(self.polygons), list(self.uvMaps.keys())))

    def transferMeshProperties(self, Mesh source, *, calcNewLoopProperty = None):
        if calcNewLoopProperty is not None:
            for name, uvMap in source.uvMaps.items():
                self.uvMaps[name] = calcNewLoopProperty(uvMap)

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
    cdef Vector3DList bitangents = Vector3DList(length = tangents.length)
    cdef Py_ssize_t i
    for i in range(bitangents.length):
        crossVec3(bitangents.data + i, tangents.data + i, normals.data + i)
    return bitangents
