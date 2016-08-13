from . ctypes cimport Matrix4, Vector3
from .. data_structures.lists.complex_lists cimport Vector3DList

cpdef void transformVector3DList(Vector3DList vectors, matrix)
cpdef double distanceSumOfVector3DList(Vector3DList vectors)

cdef void mixVector3DLists_LowLevel(Vector3* target, Vector3* a, Vector3* b, long arrayLength, float factor)
