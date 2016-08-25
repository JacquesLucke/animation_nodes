def importDataStructures():
    from . struct import ANStruct
    from . meshes.mesh_data import MeshData
    from . lists.polygon_indices_list import PolygonIndicesList
    from . lists.complex_lists import Vector3DList, Matrix4x4List, EdgeIndicesList
    from . lists.base_lists import FloatList, DoubleList, LongLongList, IntegerList, UShortList, CharList
    from . splines.poly_spline import PolySpline
    from . splines.bezier_spline import BezierSpline
    from . interpolation_base import InterpolationBase
    from . falloff_base import FalloffBase
    return locals()

dataStructures = importDataStructures()
__all__ = list(dataStructures.keys())
globals().update(dataStructures)
