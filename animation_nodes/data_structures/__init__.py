def importDataStructures():
    from . struct import ANStruct

    from . meshes.mesh_data import MeshData
    from . lists.clist import CList
    from . lists.polygon_indices_list import PolygonIndicesList
    from . lists.base_lists import (
        Vector3DList, Matrix4x4List, EdgeIndicesList, EulerList, BooleanList,
        FloatList, DoubleList, LongLongList, IntegerList, UShortList, CharList,
        QuaternionList)

    from . splines.poly_spline import PolySpline
    from . list_mocks.clist_mock import CListMock
    from . splines.bezier_spline import BezierSpline
    from . interpolation import Interpolation
    from . falloffs.falloff_base import Falloff, BaseFalloff, CompoundFalloff

    from . sounds.sound import Sound
    from . sounds.average_sound import AverageSound

    return locals()

dataStructures = importDataStructures()
__all__ = list(dataStructures.keys())
globals().update(dataStructures)
