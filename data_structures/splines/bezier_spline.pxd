from . base_spline cimport Spline
from .. lists.complex_lists cimport Vector3DList

cdef class BezierSpline(Spline):
    cdef:
        Vector3DList points
        Vector3DList leftHandles
        Vector3DList rightHandles
