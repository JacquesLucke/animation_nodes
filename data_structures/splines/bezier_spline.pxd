from . base_spline cimport Spline
from ... math.ctypes cimport Vector3
from .. lists.complex_lists cimport Vector3DList

cdef class BezierSpline(Spline):
    cdef:
        Vector3DList points
        Vector3DList leftHandles
        Vector3DList rightHandles

    cdef void getSegmentData(self, float parameter, float* t, Vector3** w)
    cdef void calcPointIndicesAndMixFactor(self, float t, long* index, float* factor)
