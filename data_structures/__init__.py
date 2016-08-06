def importDataStructures():
    from . struct import ANStruct
    from . lists.base_lists import FloatList, DoubleList, LongLongList, IntegerList, UShortList, CharList
    from . lists.complex_lists import Vector3DList
    return locals()

dataStructures = importDataStructures()
__all__ = list(dataStructures.keys())
globals().update(dataStructures)
