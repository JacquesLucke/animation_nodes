import bpy
import bmesh
import itertools
from mathutils import Vector

from . lists.complex_lists cimport Vector3DList, EdgeIndicesList

cdef class MeshData:
    cdef:
        Vector3DList vertices
        EdgeIndicesList edges
        list polygons

    def __cinit__(self, Vector3DList vertices, EdgeIndicesList edges, list polygons):
        self.vertices = vertices
        self.edges = edges
        self.polygons = polygons

    def __repr__(self):
        return "<AN Mesh Data Object: Vertices: {}, Edges: {}, Polygons: {}>".format(
                len(self.vertices), len(self.edges), len(self.polygons))

    def copy(self):
        return MeshData(self.vertices.copy(), self.edges.copy(), copy2dList(self.polygons))

    def isValid(self):
        try:
            if self.edges.base.getMaxValue() >= len(self.vertices): return False
            if not self.hasValidPolygonTupleLengths(): return False
            if not self.hasValidPolygonIndices(): return False
        except:
            return False
        return True


    def hasValidPolygonTupleLengths(self):
        polygonTupleLengths = set(map(len, self.polygons))
        return all(amount >= 3 for amount in polygonTupleLengths)

    def hasValidPolygonIndices(self):
        maxPolygonIndex = max(itertools.chain([-1], *self.polygons))
        minPolygonIndex = min(itertools.chain([0], *self.polygons))
        return 0 <= minPolygonIndex <= maxPolygonIndex <= len(self.vertices)


def copyVectorList(list):
    return [vertex.copy() for vertex in list]

def copy2dList(list):
    return [element[:] for element in list]
