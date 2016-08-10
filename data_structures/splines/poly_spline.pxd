from . base_spline cimport Spline
from ... math.ctypes cimport Vector3
from .. lists.complex_lists cimport Vector3DList

cdef class PolySpline(Spline):
    cdef:
        readonly Vector3DList points
