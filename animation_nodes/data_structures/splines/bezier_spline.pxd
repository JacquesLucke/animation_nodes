from ... math cimport Vector3
from . base_spline cimport Spline
from .. lists.base_lists cimport Vector3DList, FloatList

cdef class BezierSpline(Spline):
    cdef:
        readonly Vector3DList points
        readonly Vector3DList leftHandles
        readonly Vector3DList rightHandles
        readonly FloatList radii

    cdef void getSegmentData(self, float parameter, float* t, Vector3** w)
    cpdef calculateSmoothHandles(self, float strength = ?)
    cdef inline int getSegmentAmount(self)
