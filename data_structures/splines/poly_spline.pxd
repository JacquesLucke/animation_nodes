from ... math cimport Vector3
from . base_spline cimport Spline
from .. lists.base_lists cimport FloatList
from .. lists.complex_lists cimport Vector3DList

cdef class PolySpline(Spline):
    cdef:
        readonly Vector3DList points

    cpdef FloatList getUniformParameters(self, long amount)
    cdef inline int getSegmentAmount(self)
