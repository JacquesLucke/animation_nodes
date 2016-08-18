ctypedef float (*InterpolationFunction)(InterpolationBase, float)

cdef class InterpolationBase:
    cdef:
        InterpolationFunction function

    cdef float evaluate(self, float x)
