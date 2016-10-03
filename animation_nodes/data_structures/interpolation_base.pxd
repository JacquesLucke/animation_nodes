ctypedef double (*InterpolationFunction)(InterpolationBase, double)

cdef class InterpolationBase:
    cdef bint clamped    
    cdef double evaluate(self, double x)
