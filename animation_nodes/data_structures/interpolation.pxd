ctypedef double (*InterpolationFunction)(Interpolation, double)

cdef class Interpolation:
    cdef bint clamped    
    cdef double evaluate(self, double x)
