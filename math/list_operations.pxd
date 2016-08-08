from . conversion cimport toMatrix4
from . ctypes cimport Matrix4, Vector3
from . base_operations cimport transformVec3, distanceVec3
from .. data_structures.lists.complex_lists cimport Vector3DList

cpdef void transformVector3DList(Vector3DList vectors, matrix)
cpdef double distanceSumOfVector3DList(Vector3DList vectors)
