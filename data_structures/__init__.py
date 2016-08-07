def importDataStructures():
    from . struct import ANStruct
    from . meshes.mesh_data import MeshData
    from . lists.base_lists import FloatList, DoubleList, LongLongList, IntegerList, UShortList, CharList
    from . lists.complex_lists import Vector3DList, Matrix4x4List, EdgeIndicesList
    return locals()

dataStructures = importDataStructures()
__all__ = list(dataStructures.keys())
globals().update(dataStructures)
