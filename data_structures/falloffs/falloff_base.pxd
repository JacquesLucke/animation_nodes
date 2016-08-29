cdef class Falloff:
    cdef bint clamped

cdef class BaseFalloff(Falloff):
    cdef str dataType
    cdef double evaluate(self, void* object, long index)

cdef class CompoundFalloff(Falloff):
    cdef list getDependencies(self)
    cdef list getClampingRequirements(self)
    cdef double evaluate(self, double* dependencyResults)
