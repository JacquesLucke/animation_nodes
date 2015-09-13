import bpy
import bmesh
from mathutils import Vector

class MeshData:
    def __init__(self, vertices, edges, polygons):
        self.vertices = vertices
        self.edges = edges
        self.polygons = polygons

    def copy(self):
        return MeshData(copyVectorList(self.vertices), copy2dList(self.edges), copy2dList(self.polygons))


class Polygon:
    __slots__ = ("vertices", "normal", "center", "area", "materialIndex")

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
