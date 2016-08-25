from . falloff_base cimport Falloff, BaseFalloff, CompoundFalloff
from ... math cimport Matrix4, Vector3

cpdef createFalloffEvaluator(falloff, str sourceType)

ctypedef double (*FalloffBaseEvaluatorWithConversion)(BaseFalloff, void*, long index)

cdef class FalloffEvaluator:
    cdef readonly bint isValid

    cdef double evaluate(self, void* value, long index)

cdef class BaseFalloffEvaluator_NoConversion(FalloffEvaluator):
    cdef BaseFalloff falloff

cdef class BaseFalloffEvaluator_Conversion(FalloffEvaluator):
    cdef:
        BaseFalloff falloff
        FalloffBaseEvaluatorWithConversion evaluator
