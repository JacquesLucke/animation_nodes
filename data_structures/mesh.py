import bpy
import bmesh
from mathutils import Vector

class MeshData:
    __slots__ = ("vertices", "edges", "polygons")

    def __init__(self, vertices, edges, polygons):
        self.vertices = vertices
        self.edges = edges
        self.polygons = polygons

    def copy(self):
        return MeshData(copyVectorList(self.vertices), copy2dList(self.edges), copy2dList(self.polygons))


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
    __slots__ = ("vertices", "normal", "center", "area", "materialIndex")

    @staticmethod
    def fromMeshPolygonInLocalSpace(meshPolygon, vertexLocations):
        vertices = [vertexLocations[index].copy() for index in meshPolygon.vertices]
        return Polygon(
                 vertices,
                 meshPolygon.normal.copy(),
                 meshPolygon.center.copy(),
                 meshPolygon.area,
                 meshPolygon.material_index)

    @staticmethod
    def fromMeshPolygonInWorldSpace(meshPolygon, vertexLocations, transformation, normalTransformation, scale):
        vertices = [vertexLocations[index].copy() for index in meshPolygon.vertices]
        return Polygon(
                 vertices,
                 normalTransformation * meshPolygon.normal,
                 transformation * meshPolygon.center,
                 meshPolygon.area * scale,
                 meshPolygon.material_index)

    def __init__(self, vertices, normal, center, area, materialIndex):
        self.vertices = vertices
        self.normal = normal
        self.center = center
        self.area = area
        self.materialIndex = materialIndex

    def copy(self):
        return Polygon(copyVectorList(self.vertices), self.normal.copy(),
                       self.center, self.area, self.materialIndex)


def copyVectorList(list):
    return [vertex.copy() for vertex in list]

def copy2dList(list):
    return [element[:] for element in list]
