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
        polygonTupleLengths = set(map(len, self.polygons))
        return all(amount >= 3 for amount in polygonTupleLengths)

    def hasValidIndices(self):
        maxEdgeIndex = max(itertools.chain([-1], *self.edges))
        maxPolygonIndex = max(itertools.chain([-1], *self.polygons))

        minEdgeIndex = min(itertools.chain([0], *self.edges))
        minPolygonIndex = min(itertools.chain([0], *self.polygons))

        return max(maxEdgeIndex, maxPolygonIndex) < len(self.vertices) and min(minEdgeIndex, minPolygonIndex) >= 0


def copyVectorList(list):
    return [vertex.copy() for vertex in list]

def copy2dList(list):
    return [element[:] for element in list]
