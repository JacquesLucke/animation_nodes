from .. cimport Vector3DList, EdgeIndicesList, PolygonIndicesList

cdef class MeshData:
    cdef:
        readonly Vector3DList vertices
        readonly EdgeIndicesList edges
        readonly PolygonIndicesList polygons
