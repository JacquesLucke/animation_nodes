from .. lists.polygon_indices_list cimport PolygonIndicesList
from .. lists.base_lists cimport Vector3DList, EdgeIndicesList, LongList

cdef class Mesh:
    cdef:
        readonly Vector3DList vertices
        readonly EdgeIndicesList edges
        readonly PolygonIndicesList polygons
        readonly LongList materialIndices
        dict derivedMeshDataCache
        object uvMaps
        object vertexColorLayers

