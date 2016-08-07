import itertools
from .. lists.complex_lists cimport Vector3DList, EdgeIndicesList

cdef class MeshData:
    cdef:
        readonly Vector3DList vertices
        readonly EdgeIndicesList edges
        readonly list polygons

    def __cinit__(self, Vector3DList vertices = None,
                        EdgeIndicesList edges = None,
                        list polygons = None):

        if vertices is None: vertices = Vector3DList()
        if edges is None: edges = EdgeIndicesList()
        if polygons is None: polygons = list()

        self.vertices = vertices
        self.edges = edges
        self.polygons = polygons

    def __repr__(self):
        return "<AN Mesh Data Object: Vertices: {}, Edges: {}, Polygons: {}>".format(
                len(self.vertices), len(self.edges), len(self.polygons))

    def copy(self):
        return MeshData(self.vertices.copy(), self.edges.copy(), copy2dList(self.polygons))

    def isValid(self):
        if len(self.edges) > 0:
            if self.edges.base.getMaxValue() >= len(self.vertices):
                return False
        try:
            if not self.hasValidPolygonTupleLengths(): return False
            if not self.hasValidPolygonIndices(): return False
        except:
            return False
        return True

    def hasValidPolygonTupleLengths(self):
        polygonTupleLengths = set(map(len, self.polygons))
        return all(amount >= 3 for amount in polygonTupleLengths)

    def hasValidPolygonIndices(self):
        minPolygonIndex = min(itertools.chain([0], *self.polygons))
        maxPolygonIndex = max(itertools.chain([-1], *self.polygons))
        return 0 <= minPolygonIndex and maxPolygonIndex < len(self.vertices)


def copyVectorList(list):
    return [vertex.copy() for vertex in list]

def copy2dList(list):
    return [element[:] for element in list]
