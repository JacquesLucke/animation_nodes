import itertools
from .. lists.polygon_indices_list cimport PolygonIndicesList
from .. lists.complex_lists cimport Vector3DList, EdgeIndicesList

cdef class MeshData:
    cdef:
        readonly Vector3DList vertices
        readonly EdgeIndicesList edges
        readonly PolygonIndicesList polygons

    def __cinit__(self, Vector3DList vertices = None,
                        EdgeIndicesList edges = None,
                        PolygonIndicesList polygons = None):

        if vertices is None: vertices = Vector3DList()
        if edges is None: edges = EdgeIndicesList()
        if polygons is None: polygons = PolygonIndicesList()

        self.vertices = vertices
        self.edges = edges
        self.polygons = polygons

    def copy(self):
        return MeshData(self.vertices.copy(), self.edges.copy(), self.polygons.copy())

    def isValid(self):
        if len(self.edges) > 0:
            if self.edges.base.getMaxValue() >= len(self.vertices):
                return False
        if len(self.polygons) > 0:
            if self.polygons.indices.getMaxValue() >= len(self.vertices):
                return False
        return True

    def __repr__(self):
        return "<AN Mesh Data Object: Vertices: {}, Edges: {}, Polygons: {}>".format(
                len(self.vertices), len(self.edges), len(self.polygons))
