from . base_spline cimport Spline
from ... math.ctypes cimport Vector3
from .. lists.base_lists cimport FloatList
from .. lists.complex_lists cimport Vector3DList

cdef class PolySpline(Spline):
    cdef:
        readonly Vector3DList points

    cpdef FloatList getEqualDistanceParameters(self, long amount)
