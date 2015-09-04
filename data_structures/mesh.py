import bpy
import bmesh
from mathutils import Vector

class MeshData:
    def __init__(self, vertices, edges, polygons):
        self.vertices = vertices
        self.edges = edges
        self.polygons = polygons

    def copy(self):
        return MeshData(self.getVerticesCopy(), self.getEdgesCopy(), self.getPolygonsCopy())

    def getVerticesCopy(self):
        return [vertex.copy() for vertex in self.vertices]
    def getEdgesCopy(self):
        return copy2dList(self.edges)
    def getPolygonsCopy(self):
        return copy2dList(self.polygons)

def copy2dList(list):
    return [element[:] for element in list]
