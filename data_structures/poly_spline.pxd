from . base_spline cimport Spline
from .. math.ctypes cimport Vector3
from . lists.complex_lists cimport Vector3DList

cdef class PolySpline(Spline):
    cdef:
        Vector3DList points
        
    cdef void evaluate_LowLevel(self, float t, Vector3* result)
    cdef void calcPointIndicesAndMixFactor(self, float t, long* index, float* factor)
