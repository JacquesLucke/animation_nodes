cdef class Falloff:
    pass

cdef class BaseFalloff(Falloff):
    cdef str dataType
    cdef double evaluate(self, void* object, long index)

cdef class CompoundFalloff(Falloff):
    cdef list getDependencies(self)
