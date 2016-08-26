from cpython.ref cimport PyObject
from cpython.mem cimport PyMem_Malloc, PyMem_Free

from ... math cimport Matrix4, Vector3
from . falloff_base cimport Falloff, BaseFalloff, CompoundFalloff

ctypedef double (*BaseEvaluatorWithConversion)(BaseFalloff, void*, long index)
ctypedef double (*FalloffEvaluatorFunction)(void* settings, void* value, long index)


# Interface for other files
#########################################################

cdef class FalloffEvaluator:
    cdef double evaluate(self, void* value, long index):
        raise NotImplementedError()

cpdef createFalloffEvaluator(falloff, str sourceType):
    cdef:
        FalloffEvaluatorFunctionEvaluator evaluator
        FalloffEvaluatorFunction function
        void* settings

    createEvaluatorFunction(falloff, sourceType, &function, &settings)
    if function != NULL:
        evaluator = FalloffEvaluatorFunctionEvaluator()
        evaluator.function = function
        evaluator.settings = settings
        return evaluator
    else:
        return None


# Create Falloff Evaluators
#########################################################

cdef createEvaluatorFunction(falloff, str sourceType, FalloffEvaluatorFunction* outFunction, void** outSettings):
    outFunction[0] = NULL
    outSettings[0] = NULL

    if isinstance(falloff, BaseFalloff):
        dataType = (<BaseFalloff>falloff).dataType
        if dataType == "All" or sourceType == dataType:
            createEvaluator_NoConversion(falloff, outFunction, outSettings)
        else:
            createEvaluator_Conversion(falloff, sourceType, outFunction, outSettings)
    elif isinstance(falloff, CompoundFalloff):
        createEvaluator_Compound(falloff, sourceType, outFunction, outSettings)

cdef createEvaluator_NoConversion(BaseFalloff falloff, FalloffEvaluatorFunction* outFunction, void** outSettings):
    cdef BaseSettings_NoConversion* settings
    settings = <BaseSettings_NoConversion*>PyMem_Malloc(sizeof(BaseSettings_NoConversion))
    settings.falloff = <PyObject*>falloff
    outFunction[0] = evaluateBaseFalloff_NoConversion
    outSettings[0] = settings

cdef createEvaluator_Conversion(BaseFalloff falloff, str sourceType, FalloffEvaluatorFunction* outFunction, void** outSettings):
    cdef BaseEvaluatorWithConversion evaluator
    evaluator = getEvaluatorWithConversion(sourceType, falloff.dataType)
    if evaluator == NULL: return

    settings = <BaseSettings_Conversion*>PyMem_Malloc(sizeof(BaseSettings_Conversion))
    settings.falloff = <PyObject*>falloff
    settings.evaluator = evaluator
    outFunction[0] = evaluateBaseFalloff_Conversion
    outSettings[0] = settings

cdef createEvaluator_Compound(CompoundFalloff falloff, str sourceType, FalloffEvaluatorFunction* outFunction, void** outSettings):
    cdef:
        CompoundSettings* settings = <CompoundSettings*>PyMem_Malloc(sizeof(CompoundSettings))
        list dependencies = falloff.getDependencies()
        int amount = len(dependencies)
        int i

    settings.falloff = <PyObject*>falloff
    settings.dependencyAmount = amount
    settings.dependencyResults = <double*>PyMem_Malloc(sizeof(double) * amount)
    settings.dependencySettings = <void**>PyMem_Malloc(sizeof(char*) * amount)
    settings.dependencyFunctions = <FalloffEvaluatorFunction*>PyMem_Malloc(sizeof(FalloffEvaluatorFunction) * amount)

    for i in range(amount):
        createEvaluatorFunction(dependencies[i], sourceType, settings.dependencyFunctions + i, settings.dependencySettings + i)

    outFunction[0] = evaluateCompoundFalloff
    outSettings[0] = settings


# Free Falloff Evaluators
#########################################################

cdef freeEvaluatorFunction(FalloffEvaluatorFunction function, void* settings):
    if function == evaluateBaseFalloff_NoConversion:
        PyMem_Free(settings)
    elif function == evaluateBaseFalloff_Conversion:
        PyMem_Free(settings)
    elif function == evaluateCompoundFalloff:
        freeCompoundSettings(<CompoundSettings*>settings)

cdef freeCompoundSettings(CompoundSettings* settings):
    cdef int i
    for i in range(settings.dependencyAmount):
        freeEvaluatorFunction(settings.dependencyFunctions[i], settings.dependencySettings[i])

    PyMem_Free(settings.dependencyResults)
    PyMem_Free(settings.dependencyFunctions)
    PyMem_Free(settings.dependencySettings)
    PyMem_Free(settings)


# Evaluator Settings
#########################################################

cdef struct BaseSettings_NoConversion:
    PyObject* falloff

cdef struct BaseSettings_Conversion:
    PyObject* falloff
    BaseEvaluatorWithConversion evaluator

cdef struct CompoundSettings:
    PyObject* falloff
    FalloffEvaluatorFunction* dependencyFunctions
    void** dependencySettings
    double* dependencyResults
    int dependencyAmount


# Execute Falloff Evaluators
#########################################################

cdef double evaluateBaseFalloff_NoConversion(void* settings, void* value, long index):
    cdef BaseSettings_NoConversion* _settings = <BaseSettings_NoConversion*>settings
    return (<BaseFalloff>_settings.falloff).evaluate(value, index)

cdef double evaluateBaseFalloff_Conversion(void* settings, void* value, long index):
    cdef BaseSettings_Conversion* _settings = <BaseSettings_Conversion*>settings
    return _settings.evaluator(<BaseFalloff>_settings.falloff, value, index)

cdef double evaluateCompoundFalloff(void* settings, void* value, long index):
    cdef CompoundSettings* _settings = <CompoundSettings*>settings
    cdef int i
    for i in range(_settings.dependencyAmount):
        _settings.dependencyResults[i] = _settings.dependencyFunctions[i](_settings.dependencySettings[i], value, index)
    return (<CompoundFalloff>_settings.falloff).evaluate(_settings.dependencyResults)


# Evaluator Function Wrapper
#########################################################

cdef class FalloffEvaluatorFunctionEvaluator(FalloffEvaluator):
    cdef FalloffEvaluatorFunction function
    cdef void* settings

    def __dealloc__(self):
        freeEvaluatorFunction(self.function, self.settings)

    cdef double evaluate(self, void* value, long index):
        return self.function(self.settings, value, index)


# Value Conversion
###########################################################

cdef BaseEvaluatorWithConversion getEvaluatorWithConversion(str sourceType, str targetType):
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
