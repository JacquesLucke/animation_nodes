import bpy
import bmesh
import itertools
from mathutils import Vector

class MeshData:
    __slots__ = ("vertices", "edges", "polygons")

    def __init__(self, vertices, edges, polygons):
        self.vertices = vertices
        self.edges = edges
        self.polygons = polygons

    def __repr__(self):
        return "<AN Mesh Data Object: Vertices: {}, Edges: {}, Polygons: {}>".format(
                len(self.vertices), len(self.edges), len(self.polygons))

    def copy(self):
        return MeshData(copyVectorList(self.vertices), copy2dList(self.edges), copy2dList(self.polygons))

    def isValid(self, checkTupleLengths = True, checkIndices = True):
        try:
            if checkTupleLengths:
                if not self.hasValidEdgeTupleLengths(): return False
                if not self.hasValidPolygonTupleLengths(): return False
            if checkIndices:
                if not self.hasValidIndices(): return False
        except:
            return False
        return True

    def hasValidEdgeTupleLengths(self):
        checkTuple = tuple([2] * len(self.edges))
        edgeTupleLengths = tuple(map(len, self.edges))
        return checkTuple == edgeTupleLengths

    def hasValidPolygonTupleLengths(self):
        return all(amount >= 3 for amount in map(len, self.polygons))

    def hasValidIndices(self):
        maxEdgeIndex = max(itertools.chain([-1], *self.edges))
        maxPolygonIndex = max(itertools.chain([-1], *self.polygons))

        minEdgeIndex = min(itertools.chain([0], *self.edges))
        minPolygonIndex = min(itertools.chain([0], *self.polygons))

        return max(maxEdgeIndex, maxPolygonIndex) < len(self.vertices) and min(minEdgeIndex, minPolygonIndex) >= 0




class Vertex:
    __slots__ = ("location", "normal", "groupWeights")

    @staticmethod
    def fromMeshVertexInLocalSpace(meshVertex):
        return Vertex(
                 meshVertex.co.copy(),
                 meshVertex.normal.copy(),
                 [group.weight for group in meshVertex.groups])

    @staticmethod
    def fromMeshVertexInWorldSpace(meshVertex, vertexTransformation, normalTransformation):
        return Vertex(
                 vertexTransformation * meshVertex.co,
                 normalTransformation * meshVertex.normal,
                 [group.weight for group in meshVertex.groups])

    def __init__(self, location, normal, groupWeights):
        self.location = location
        self.normal = normal
        self.groupWeights = groupWeights

    def copy(self):
        return Vertex(self.location.copy(), self.normal.copy(), self.groupWeights[:])


class Polygon:
    __slots__ = ("vertexLocations", "normal", "center", "area", "materialIndex")

    @staticmethod
    def fromMeshPolygonInLocalSpace(meshPolygon, allVertexLocations):
        vertexLocations = [allVertexLocations[index].copy() for index in meshPolygon.vertices]
        return Polygon(
                 vertexLocations,
                 meshPolygon.normal.copy(),
                 meshPolygon.center.copy(),
                 meshPolygon.area,
                 meshPolygon.material_index)

    @staticmethod
    def fromMeshPolygonInWorldSpace(meshPolygon, allVertexLocations, transformation, normalTransformation, scale):
        vertexLocations = [allVertexLocations[index].copy() for index in meshPolygon.vertices]
        return Polygon(
                 vertexLocations,
                 normalTransformation * meshPolygon.normal,
                 transformation * meshPolygon.center,
                 meshPolygon.area * scale,
                 meshPolygon.material_index)

    def __init__(self, vertexLocations, normal, center, area, materialIndex):
        self.vertexLocations = vertexLocations
        self.normal = normal
        self.center = center
        self.area = area
        self.materialIndex = materialIndex

    def copy(self):
        return Polygon(copyVectorList(self.vertexLocations), self.normal.copy(),
                       self.center, self.area, self.materialIndex)

    def __repr__(self):
        return "<Polygon - Center: ({:.3f}, {:.3f}, {:.3f}), Verts: {}>".format(
            self.center.x, self.center.y, self.center.z, len(self.vertexLocations))


def copyVectorList(list):
    return [vertex.copy() for vertex in list]

def copy2dList(list):
    return [element[:] for element in list]
