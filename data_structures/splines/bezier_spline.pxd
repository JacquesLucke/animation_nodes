from ... math cimport Vector3
from . base_spline cimport Spline
from .. lists.complex_lists cimport Vector3DList

cdef class BezierSpline(Spline):
    cdef:
        readonly Vector3DList points
        readonly Vector3DList leftHandles
        readonly Vector3DList rightHandles

    cpdef appendPoint(self, point, leftHandle, rightHandle)

    cdef void getSegmentData(self, float parameter, float* t, Vector3** w)

    cpdef calculateSmoothHandles(self, float strength = ?)
