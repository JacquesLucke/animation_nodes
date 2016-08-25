cdef class FalloffEvaluator:
    cdef double evaluate(self, void* value, long index):
        raise NotImplementedError()

cdef class SimpleFalloffBaseEvaluator(FalloffEvaluator):
    def __cinit__(self, FalloffBase falloff):
        self.falloff = falloff
        self.isValid = True

    cdef double evaluate(self, void* value, long index):
        return self.falloff.evaluate(value, index)

cdef class ComplexFalloffBaseEvaluator(FalloffEvaluator):
    def __cinit__(self, FalloffBase falloff, str sourceType):
        cdef str dataType = falloff.getHandledDataType()
        self.evaluator = getConverter(sourceType, dataType)
        self.falloff = falloff
        self.isValid = self.evaluator != NULL

    cdef double evaluate(self, void* value, long index):
        return self.evaluator(self.falloff, value, index)

cpdef getFalloffEvaluator(falloff, str sourceType):
    cdef FalloffEvaluator evaluator

    if isinstance(falloff, FalloffBase):
        dataType = falloff.getHandledDataType()
        if dataType == "All" or sourceType == dataType:
            evaluator = SimpleFalloffBaseEvaluator(falloff)
        else:
            evaluator = ComplexFalloffBaseEvaluator(falloff, sourceType)

    if getattr(evaluator, "isValid", False):
        return evaluator
    return None

cdef FalloffBaseEvaluatorWithConversion getConverter(str sourceType, str targetType):
    if sourceType == "Transformation Matrix" and targetType == "Location":
        return convert_TransformationMatrix_Location
    return NULL

from ... math cimport Matrix4, Vector3
cdef double convert_TransformationMatrix_Location(FalloffBase falloff, void* value, long index):
    cdef Matrix4* matrix = <Matrix4*>value
    cdef Vector3 vector
    vector.x = matrix.a14
    vector.y = matrix.a24
    vector.z = matrix.a34
    return falloff.evaluate(&vector, index)
