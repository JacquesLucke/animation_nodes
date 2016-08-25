from . falloff_base cimport FalloffBase
from ... math cimport Matrix4, Vector3

cpdef createFalloffEvaluator(falloff, str sourceType)

ctypedef double (*FalloffBaseEvaluatorWithConversion)(FalloffBase, void*, long index)

cdef class FalloffEvaluator:
    cdef readonly bint isValid

    cdef double evaluate(self, void* value, long index)

cdef class SimpleFalloffBaseEvaluator(FalloffEvaluator):
    cdef FalloffBase falloff

cdef class ComplexFalloffBaseEvaluator(FalloffEvaluator):
    cdef:
        FalloffBase falloff
        FalloffBaseEvaluatorWithConversion evaluator
