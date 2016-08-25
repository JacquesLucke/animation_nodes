from cpython.mem cimport PyMem_Malloc, PyMem_Free

cpdef createFalloffEvaluator(falloff, str sourceType):
    cdef BaseFalloff _falloffBase
    evaluator = None

    if isinstance(falloff, BaseFalloff):
        _falloffBase = falloff
        dataType = _falloffBase.dataType
        if dataType == "All" or sourceType == dataType:
            evaluator = BaseFalloffEvaluator_NoConversion(_falloffBase)
        else:
            evaluator = BaseFalloffEvaluator_Conversion(_falloffBase, sourceType)
    elif isinstance(falloff, CompoundFalloff):
        evaluator = CompoundFalloffEvaluator(falloff, sourceType)

    if getattr(evaluator, "isValid", False):
        return evaluator
    else:
        return None


cdef class FalloffEvaluator:
    cdef double evaluate(self, void* value, long index):
        raise NotImplementedError()


cdef class BaseFalloffEvaluator_NoConversion(FalloffEvaluator):
    def __cinit__(self, BaseFalloff falloff):
        self.falloff = falloff
        self.isValid = True

    cdef double evaluate(self, void* value, long index):
        return self.falloff.evaluate(value, index)


cdef class BaseFalloffEvaluator_Conversion(FalloffEvaluator):
    def __cinit__(self, BaseFalloff falloff, str sourceType):
        self.evaluator = getEvaluatorWithConversion(sourceType, falloff.dataType)
        self.isValid = self.evaluator != NULL
        self.falloff = falloff

    cdef double evaluate(self, void* value, long index):
        return self.evaluator(self.falloff, value, index)


cdef class CompoundFalloffEvaluator(FalloffEvaluator):
    cdef:
        int dependencyAmount
        double* dependencyResults
        list dependencyEvaluators
        CompoundFalloff falloff

    def __cinit__(self, CompoundFalloff falloff not None, str sourceType):
        cdef:
            list dependencies = falloff.getDependencies()
            Falloff dependencyFalloff
            FalloffEvaluator evaluator
        self.isValid = True
        self.dependencyAmount = len(dependencies)
        self.dependencyEvaluators = []
        for dependencyFalloff in dependencies:
            evaluator = createFalloffEvaluator(dependencyFalloff, sourceType)
            if evaluator is None:
                self.isValid = False
                break
            else:
                self.dependencyEvaluators.append(evaluator)
        if self.isValid:
            self.dependencyResults = <double*>PyMem_Malloc(sizeof(double) * self.dependencyAmount)
            self.falloff = falloff

    def __dealloc__(self):
        if self.dependencyResults != NULL:
            PyMem_Free(self.dependencyResults)

    cdef double evaluate(self, void* value, long index):
        cdef:
            int i
            FalloffEvaluator evaluator
        for i in range(self.dependencyAmount):
            evaluator = self.dependencyEvaluators[i]
            self.dependencyResults[i] = evaluator.evaluate(value, index)
        return self.falloff.evaluate(self.dependencyResults)


# Value Conversion
###########################################################

cdef FalloffBaseEvaluatorWithConversion getEvaluatorWithConversion(str sourceType, str targetType):
    if sourceType == "Transformation Matrix" and targetType == "Location":
        return convert_TransformationMatrix_Location
    return NULL

cdef double convert_TransformationMatrix_Location(BaseFalloff falloff, void* value, long index):
    cdef Matrix4* matrix = <Matrix4*>value
    cdef Vector3 vector
    vector.x = matrix.a14
    vector.y = matrix.a24
    vector.z = matrix.a34
    return falloff.evaluate(&vector, index)
