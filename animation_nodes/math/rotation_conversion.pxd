from .. data_structures.lists.base_lists cimport EulerList, Matrix4x4List

cdef matrixToEuler(Euler3* target, Matrix3_or_Matrix4* m)
