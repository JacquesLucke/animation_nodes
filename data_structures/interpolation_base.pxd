ctypedef double (*InterpolationFunction)(InterpolationBase, double)

cdef class InterpolationBase:
    cdef double evaluate(self, double x)
