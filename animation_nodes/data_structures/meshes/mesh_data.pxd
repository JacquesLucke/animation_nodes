from .. lists.base_lists cimport Vector3DList, EdgeIndicesList
from .. lists.polygon_indices_list cimport PolygonIndicesList

cdef class Mesh:
    cdef:
        readonly Vector3DList vertices
        readonly EdgeIndicesList edges
        readonly PolygonIndicesList polygons
        dict derivedMeshDataCache
        dict vertexProperties
        dict edgeProperties
        dict polygonProperties
        dict loopProperties
        dict uvMaps
