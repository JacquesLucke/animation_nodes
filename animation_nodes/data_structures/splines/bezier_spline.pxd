from ... math cimport Vector3
from . base_spline cimport Spline
from .. lists.base_lists cimport Vector3DList, FloatList

cdef class BezierSpline(Spline):
    cdef:
        public Vector3DList points
        public Vector3DList leftHandles
        public Vector3DList rightHandles
        public FloatList radii
        public FloatList tilts
        Vector3DList normalsCache
