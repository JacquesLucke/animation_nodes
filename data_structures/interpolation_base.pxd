ctypedef double (*InterpolationFunction)(InterpolationBase, double)

cdef class InterpolationBase:
    cdef:
        InterpolationFunction function

    cdef double evaluate(self, double x)
