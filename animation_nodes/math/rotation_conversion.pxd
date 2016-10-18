from .. data_structures.lists.base_lists cimport EulerList, Matrix4x4List
from . matrix cimport Matrix3_or_Matrix4
from . euler cimport Euler3

cdef matrixToEuler(Euler3* target, Matrix3_or_Matrix4* m)
