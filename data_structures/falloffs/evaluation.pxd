from . falloff_base cimport Falloff, BaseFalloff, CompoundFalloff
from ... math cimport Matrix4, Vector3

cpdef createFalloffEvaluator(falloff, str sourceType)

ctypedef double (*BaseEvaluatorWithConversion)(BaseFalloff, void*, long index)
ctypedef double (*FalloffEvaluatorFunction)(void* settings, void* value, long index)

cdef class FalloffEvaluator:
    cdef readonly bint isValid

    cdef double evaluate(self, void* value, long index)

cdef class FalloffEvaluatorFunctionEvaluator(FalloffEvaluator):
    cdef void* settings
    cdef FalloffEvaluatorFunction function
