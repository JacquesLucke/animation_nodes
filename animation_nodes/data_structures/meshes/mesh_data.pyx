# cython: profile=True
import textwrap
import functools
from .. lists.clist cimport CList
from collections import OrderedDict
from . validate import createValidEdgesList, checkMeshData, calculateLoopEdges
from .. attributes.attribute import AttributeType, AttributeDomain, AttributeDataType
from .. attributes.attribute cimport Attribute, AttributeType, AttributeDomain, AttributeDataType
from ... algorithms.mesh.triangulate_mesh import (
    triangulatePolygonsUsingFanSpanMethod,
    triangulatePolygonsUsingEarClipMethod
)
from .. lists.base_lists cimport (
    LongList,
    ColorList,
    EdgeIndices,
    UIntegerList,
    Vector2DList,
    Vector3DList,
    EdgeIndicesList,
)
from ... math cimport (
    Vector3,
    subVec3,
    crossVec3,
    normalizeVec3,
    addVec3_Inplace,
    isExactlyZeroVec3,
    Matrix4, toMatrix4,
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

        self.builtInAttributes = OrderedDict()
        self.customAttributes = OrderedDict()
        self.uvMapAttributes = OrderedDict()
        self.vertexColorAttributes = OrderedDict()
        self.vertexWeightAttributes = OrderedDict()

    def getAttributeDictionaries(self):
        return (
            self.builtInAttributes,
            self.customAttributes,
            self.uvMapAttributes,
            self.vertexColorAttributes,
            self.vertexWeightAttributes,
        )

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


    def insertBuiltInAttribute(self, Attribute attribute):
        if self.getAttributeDomainLength(attribute.domain) != len(attribute.data):
            raise Exception("invalid length")
        self.builtInAttributes[attribute.name] = attribute

    def insertUVMapAttribute(self, Attribute attribute):
        if self.getAttributeDomainLength(attribute.domain) != len(attribute.data):
            raise Exception("invalid length")
        self.uvMapAttributes[attribute.name] = attribute

    def insertVertexColorAttribute(self, Attribute attribute):
        if self.getAttributeDomainLength(attribute.domain) != len(attribute.data):
            raise Exception("invalid length")
        self.vertexColorAttributes[attribute.name] = attribute

    def insertVertexWeightAttribute(self, Attribute attribute):
        if self.getAttributeDomainLength(attribute.domain) != len(attribute.data):
            raise Exception("invalid length")
        self.vertexWeightAttributes[attribute.name] = attribute

    def insertCustomAttribute(self, Attribute attribute):
        if self.getAttributeDomainLength(attribute.domain) != len(attribute.data):
            raise Exception("invalid length")
        self.customAttributes[attribute.name] = attribute


    def iterBuiltInAttributes(self):
        return self.builtInAttributes.values()

    def iterUVMapAttributes(self):
        return self.uvMapAttributes.values()

    def iterVertexColorAttributes(self):
        return self.vertexColorAttributes.values()

    def iterVertexWeightAttributes(self):
        return self.vertexWeightAttributes.values()

    def iterCustomAttributes(self):
        return self.customAttributes.values()


    def getAllBuiltInAttributeNames(self):
        return list(self.builtInAttributes.keys())

    def getAllUVMapAttributeNames(self):
        return list(self.uvMapAttributes.keys())

    def getAllVertexColorAttributeNames(self):
        return list(self.vertexColorAttributes.keys())

    def getAllVertexWeightAttributeNames(self):
        return list(self.vertexWeightAttributes.keys())

    def getAllCustomAttributeNames(self):
        return list(self.customAttributes.keys())


    def getBuiltInAttribute(self, str name):
        return self.builtInAttributes.get(name)

    def getUVMapAttribute(self, str name):
        return self.uvMapAttributes.get(name)

    def getVertexColorAttribute(self, str name):
        return self.vertexColorAttributes.get(name)

    def getVertexWeightAttribute(self, str name):
        return self.vertexWeightAttributes.get(name)

    def getCustomAttribute(self, str name):
        return self.customAttributes.get(name, None)


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
        mesh.copyAttributes(self)
        return mesh

    def copyAttributes(self, Mesh source):
        for (meshAttributes, sourceMeshAttributes) in zip(
             self.getAttributeDictionaries(), source.getAttributeDictionaries()):
            for name, value in sourceMeshAttributes.items():
                meshAttributes[name] = value.copy()

    def transform(self, transformation):
        self.vertices.transform(transformation)
        self.verticesTransformed()

    def move(self, translation):
        self.vertices.move(translation)
        self.verticesMoved()

    def triangulateMesh(self, str method = "FAN"):
        cdef PolygonIndicesList polygons = self.polygons
        cdef PolygonIndicesList newPolygons
        if method == "FAN":
            newPolygons = triangulatePolygonsUsingFanSpanMethod(polygons)
        elif method == "EAR":
            newPolygons = triangulatePolygonsUsingEarClipMethod(self.vertices, polygons)
        self.edges = createValidEdgesList(polygons = newPolygons)
        self.polygons = newPolygons
        self.derivedMeshDataCache.clear()
        self.builtInAttributes.clear()
        self.customAttributes.clear()
        self.uvMapAttributes.clear()
        self.vertexColorAttributes.clear()

    def __repr__(self):
        return textwrap.dedent(
        f"""AN Mesh Object:
        Vertices: {len(self.vertices)}
        Edges: {len(self.edges)}
        Polygons: {len(self.polygons)}
        UV Maps: {self.getAllUVMapAttributeNames()}
        Vertex Colors: {self.getAllVertexColorAttributeNames()}
        Vertex Groups: {self.getAllVertexWeightAttributeNames()}
        Built-In Attributes: {self.getAllBuiltInAttributeNames()}
        Custom Attributes: {self.getAllCustomAttributeNames()}""")

    def replicateAttributes(self, Mesh source, long amount):
        for (meshAttributes, sourceMeshAttributes) in zip(
             self.getAttributeDictionaries(), source.getAttributeDictionaries()):
            for name, attribute in sourceMeshAttributes.items():
                meshAttributes[name] = attribute.replicate(amount)

    def getAttributeDomainLength(self, AttributeDomain domain):
        if domain == AttributeDomain.POINT:
            return self.vertices.length
        elif domain == AttributeDomain.EDGE:
            return self.edges.length
        elif domain == AttributeDomain.FACE:
            return self.polygons.getLength()
        elif domain == AttributeDomain.CORNER:
            return self.polygons.indices.length

    def appendAttributes(self, Mesh source):
        for (meshAttributes, sourceMeshAttributes) in zip(
             self.getAttributeDictionaries(), source.getAttributeDictionaries()):

            for name, attribute in meshAttributes.items():
                sourceAttribute = sourceMeshAttributes.get(name, None)
                if sourceAttribute and sourceAttribute.similar(attribute):
                    attribute.append(sourceAttribute)
                else:
                    length = source.getAttributeDomainLength(attribute.domain)
                    attribute.appendZeros(length)

            for name, sourceAttribute in sourceMeshAttributes.items():
                attribute = meshAttributes.get(name, None)
                if attribute is None:
                    length = self.getAttributeDomainLength(sourceAttribute.domain)
                    newAttribute = sourceAttribute.copy()
                    newAttribute.prependZeros(length)
                    meshAttributes[name] = newAttribute

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

        self.appendAttributes(meshData)

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
