from ... math cimport Vector3
from . base_spline cimport Spline
from .. lists.base_lists cimport FloatList, Vector3DList

cdef class PolySpline(Spline):
    cdef:
        public Vector3DList points
        public FloatList radii
        public FloatList tilts
        Vector3DList normalsCache
