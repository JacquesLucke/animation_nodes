from cpython.mem cimport PyMem_Malloc, PyMem_Free
from cpython.ref cimport PyObject, Py_INCREF, Py_DECREF

from . falloff_base cimport Falloff
from . falloff_base cimport BaseFalloff, CompoundFalloff
from . types cimport (
    falloffDataTypeExists,
    EvaluateBaseConverted,
    isValidSourceForDataTypes,
    typeConversionRequired,
    getCallConvertedFunction,
    getPyConversionFunction,
    getSizeOfFalloffDataType,
    PyConversionFunction,
    getConvertListFunction
)

from ... utils.pointers cimport pointerToInt, intToPointer
from ... math cimport Matrix4, Vector3, toVector3, toMatrix4

ctypedef float (*EvaluatorFunction)(void *settings, void *value, Py_ssize_t index)
ctypedef void (*ListEvaluatorFunction)(void *settings, void *values, Py_ssize_t startIndex,
                                       Py_ssize_t amount, float *target)


# Interface for other files
#########################################################

from .. lists.clist cimport CList
from .. lists.base_lists cimport FloatList

cdef class FalloffEvaluator:
    @staticmethod
    def create(Falloff falloff, str sourceType, bint clamped):
        if not falloffDataTypeExists(sourceType):
            raise Exception("Unknown source type")

        cdef set dataTypes = getBaseFalloffTypes(falloff)
        if not isValidSourceForDataTypes(sourceType, dataTypes):
            raise Exception("Cannot create FalloffEvaluator for this source type")

        return createFalloffEvaluator(falloff, sourceType, clamped)

    cdef float evaluate(self, void *value, Py_ssize_t index):
        raise NotImplementedError()

    cdef pyEvaluate(self, object value, Py_ssize_t index):
        raise NotImplementedError()

    cdef void evaluateList_LowLevel(self, void *values, Py_ssize_t startIndex,
                                    Py_ssize_t amount, float *target):
        raise NotImplementedError()

    def evaluateList(self, CList values, Py_ssize_t startIndex = 0):
        cdef Py_ssize_t amount = values.getLength()
        cdef FloatList result = FloatList(length = amount)
        self.evaluateList_LowLevel(values.getPointer(), startIndex, amount, result.data)
        return result

    def __call__(self, object value, Py_ssize_t index):
        return self.pyEvaluate(value, index)


cdef class EvaluatorFunctionEvaluator(FalloffEvaluator):
    cdef void *settings
    cdef EvaluatorFunction function

    cdef void *listSettings
    cdef ListEvaluatorFunction listFunction

    cdef PyConversionFunction pyConversion
    cdef void *pyConversionBuffer

    cdef preparePyConversion(self):
        self.pyConversion = getPyConversionFunction(self.sourceType)
        self.pyConversionBuffer = PyMem_Malloc(getSizeOfFalloffDataType(self.sourceType))

    def __dealloc__(self):
        freeEvaluatorFunction(self.function, self.settings)
        freeListEvaluatorFunction(self.listFunction, self.listSettings)
        PyMem_Free(self.pyConversionBuffer)

    cdef float evaluate(self, void *value, Py_ssize_t index):
        return self.function(self.settings, value, index)

    cdef void evaluateList_LowLevel(self, void *values, Py_ssize_t startIndex,
                                    Py_ssize_t amount, float *target):
        self.listFunction(self.listSettings, values, startIndex, amount, target)

    cdef pyEvaluate(self, object value, Py_ssize_t index):
        self.pyConversion(value, self.pyConversionBuffer)
        return self.evaluate(self.pyConversionBuffer, index)


cdef createFalloffEvaluator(Falloff falloff, str sourceType, bint clamped = False):
    assert falloff is not None

    cdef:
        EvaluatorFunctionEvaluator evaluator
        EvaluatorFunction function
        void *settings
        ListEvaluatorFunction listFunction
        void *listSettings

    createEvaluatorFunction(falloff, sourceType, clamped, &function, &settings)
    createListEvaluatorFunction(falloff, sourceType, clamped, &listFunction, &listSettings)

    evaluator = EvaluatorFunctionEvaluator()
    evaluator.function = function
    evaluator.settings = settings

    evaluator.listFunction = listFunction
    evaluator.listSettings = listSettings

    evaluator.sourceType = sourceType
    evaluator.preparePyConversion()

    return evaluator


#########################################################
# Single Evaluation
#########################################################

# Create Falloff Evaluators
#########################################################

cdef createEvaluatorFunction(Falloff falloff, str sourceType, bint clamped,
                             EvaluatorFunction *outFunction, void **outSettings):
    cdef:
        EvaluatorFunction function
        void *settings

    if isinstance(falloff, BaseFalloff):
        dataType = (<BaseFalloff>falloff).dataType
        if typeConversionRequired(sourceType, (<BaseFalloff>falloff).dataType):
            createBaseEvaluator_Conversion(falloff, sourceType, &function, &settings)
        else:
            createBaseEvaluator_NoConversion(falloff, &function, &settings)
    elif isinstance(falloff, CompoundFalloff):
        dependencyAmount = len((<CompoundFalloff>falloff).getDependencies())
        if dependencyAmount == 1:
            createCompoundEvaluator_One(falloff, sourceType, &function, &settings)
        else:
            createCompoundEvaluator_Generic(falloff, sourceType, &function, &settings)

    if not falloff.clamped and clamped:
        createClampingEvaluator(function, settings, outFunction, outSettings)
    else:
        outFunction[0] = function
        outSettings[0] = settings


cdef createBaseEvaluator_NoConversion(BaseFalloff falloff,
                                      EvaluatorFunction *outFunction, void **outSettings):
    cdef BaseSettings_NoConversion *settings
    settings = <BaseSettings_NoConversion*>PyMem_Malloc(sizeof(BaseSettings_NoConversion))
    settings.falloff = <PyObject*>falloff
    outFunction[0] = evaluateBaseFalloff_NoConversion
    outSettings[0] = settings

cdef createBaseEvaluator_Conversion(BaseFalloff falloff, str sourceType,
                                    EvaluatorFunction *outFunction, void **outSettings):
    settings = <BaseSettings_Conversion*>PyMem_Malloc(sizeof(BaseSettings_Conversion))
    settings.falloff = <PyObject*>falloff
    settings.evaluator = getCallConvertedFunction(sourceType, falloff.dataType)
    outFunction[0] = evaluateBaseFalloff_Conversion
    outSettings[0] = settings

cdef createCompoundEvaluator_Generic(CompoundFalloff falloff, str sourceType,
                                     EvaluatorFunction *outFunction, void **outSettings):
    cdef:
        CompoundSettings_Generic *settings = <CompoundSettings_Generic*>PyMem_Malloc(sizeof(CompoundSettings_Generic))
        list dependencies = falloff.getDependencies()
        list clampingRequirements = falloff.getClampingRequirements()
        int amount = len(dependencies)
        int i

    settings.falloff = <PyObject*>falloff
    settings.dependencyAmount = amount
    settings.dependencyResults = <float*>PyMem_Malloc(sizeof(float) * amount)
    settings.dependencySettings = <void**>PyMem_Malloc(sizeof(void*) * amount)
    settings.dependencyFunctions = <EvaluatorFunction*>PyMem_Malloc(sizeof(EvaluatorFunction) * amount)

    for i in range(amount):
        createEvaluatorFunction(dependencies[i], sourceType, clampingRequirements[i],
            settings.dependencyFunctions + i, settings.dependencySettings + i)

    outFunction[0] = evaluateCompoundFalloff_Generic
    outSettings[0] = settings

cdef createCompoundEvaluator_One(CompoundFalloff falloff, str sourceType,
                                 EvaluatorFunction *outFunction, void **outSettings):
    cdef CompoundSettings_One *settings
    settings = <CompoundSettings_One*>PyMem_Malloc(sizeof(CompoundSettings_One))
    settings.falloff = <PyObject*>falloff
    createEvaluatorFunction(falloff.getDependencies()[0], sourceType,
        falloff.getClampingRequirements()[0],
        &settings.dependencyFunction, &settings.dependencySettings)

    outFunction[0] = evaluateCompoundFalloff_One
    outSettings[0] = settings

cdef createClampingEvaluator(EvaluatorFunction realFunction, void *realSettings,
                             EvaluatorFunction *outFunction, void **outSettings):
    cdef ClampingSettings *settings = <ClampingSettings*>PyMem_Malloc(sizeof(ClampingSettings))
    settings.realFunction = realFunction
    settings.realSettings = realSettings
    outFunction[0] = evaluateClamping
    outSettings[0] = settings


# Free Falloff Evaluators
#########################################################

cdef freeEvaluatorFunction(EvaluatorFunction function, void *settings):
    if function == evaluateBaseFalloff_NoConversion:
        PyMem_Free(settings)
    elif function == evaluateBaseFalloff_Conversion:
        PyMem_Free(settings)
    elif function == evaluateCompoundFalloff_Generic:
        freeCompoundSettings_Generic(<CompoundSettings_Generic*>settings)
    elif function == evaluateCompoundFalloff_One:
        PyMem_Free(settings)
    elif function == evaluateClamping:
        freeClampingSettings(<ClampingSettings*>settings)

cdef freeCompoundSettings_Generic(CompoundSettings_Generic *settings):
    cdef int i
    for i in range(settings.dependencyAmount):
        freeEvaluatorFunction(settings.dependencyFunctions[i], settings.dependencySettings[i])

    PyMem_Free(settings.dependencyResults)
    PyMem_Free(settings.dependencyFunctions)
    PyMem_Free(settings.dependencySettings)
    PyMem_Free(settings)

cdef freeClampingSettings(ClampingSettings *settings):
    freeEvaluatorFunction(settings.realFunction, settings.realSettings)
    PyMem_Free(settings)


# Evaluator Settings
#########################################################

cdef struct BaseSettings_NoConversion:
    PyObject *falloff

cdef struct BaseSettings_Conversion:
    PyObject *falloff
    EvaluateBaseConverted evaluator

cdef struct CompoundSettings_Generic:
    PyObject *falloff
    EvaluatorFunction *dependencyFunctions
    void **dependencySettings
    float *dependencyResults
    int dependencyAmount

cdef struct CompoundSettings_One:
    PyObject *falloff
    EvaluatorFunction dependencyFunction
    void *dependencySettings

cdef struct ClampingSettings:
    EvaluatorFunction realFunction
    void *realSettings


# Execute Falloff Evaluators
#########################################################

cdef float evaluateBaseFalloff_NoConversion(void *settings, void *value, Py_ssize_t index):
    cdef BaseSettings_NoConversion *_settings = <BaseSettings_NoConversion*>settings
    return (<BaseFalloff>_settings.falloff).evaluate(value, index)

cdef float evaluateBaseFalloff_Conversion(void *settings, void *value, Py_ssize_t index):
    cdef BaseSettings_Conversion *_settings = <BaseSettings_Conversion*>settings
    return _settings.evaluator(<BaseFalloff>_settings.falloff, value, index)

cdef float evaluateCompoundFalloff_Generic(void *settings, void *value, Py_ssize_t index):
    cdef CompoundSettings_Generic *_settings = <CompoundSettings_Generic*>settings
    cdef int i
    for i in range(_settings.dependencyAmount):
        _settings.dependencyResults[i] = _settings.dependencyFunctions[i](_settings.dependencySettings[i], value, index)
    return (<CompoundFalloff>_settings.falloff).evaluate(_settings.dependencyResults)

cdef float evaluateCompoundFalloff_One(void *settings, void *value, Py_ssize_t index):
    cdef CompoundSettings_One *_settings = <CompoundSettings_One*>settings
    cdef float dependencyResult = _settings.dependencyFunction(_settings.dependencySettings, value, index)
    return (<CompoundFalloff>_settings.falloff).evaluate(&dependencyResult)

cdef float evaluateClamping(void *settings, void *value, Py_ssize_t index):
    cdef ClampingSettings *_settings = <ClampingSettings*>settings
    cdef float result = _settings.realFunction(_settings.realSettings, value, index)
    if result > 1: return 1
    if result < 0: return 0
    return result



#########################################################
# List Evaluation
#########################################################

cdef createListEvaluatorFunction(Falloff falloff, str sourceType, bint clamped,
                                 ListEvaluatorFunction *outFunction, void **outSettings):

    cdef ListEvaluatorSettings *settings
    settings = <ListEvaluatorSettings*>PyMem_Malloc(sizeof(ListEvaluatorSettings))
    settings.falloff = <PyObject*>falloff
    settings.sourceType = <PyObject*>sourceType
    Py_INCREF(sourceType)

    outFunction[0] = evaluateList
    outSettings[0] = settings

cdef freeListEvaluatorFunction(ListEvaluatorFunction function, void *_settings):
    cdef ListEvaluatorSettings *settings = <ListEvaluatorSettings*>_settings
    Py_DECREF(<object>settings.sourceType)
    PyMem_Free(settings)

cdef struct ListEvaluatorSettings:
    PyObject *falloff
    PyObject *sourceType


cdef void evaluateList(void *_settings, void *values, Py_ssize_t startIndex,
                       Py_ssize_t amount, float *target):
    cdef ListEvaluatorSettings *settings = <ListEvaluatorSettings*>_settings
    cdef Falloff falloff = <Falloff>settings.falloff
    cdef str sourceType = <str>settings.sourceType

    cdef set dataTypes = getBaseFalloffTypes(falloff)

    cdef dict preparedLists
    cdef set listsToFree
    preparedLists, listsToFree = getListsForDataTypes(sourceType, dataTypes, values, amount)

    evaluateList_UnknownType(falloff, preparedLists, startIndex, amount, target)

    freeListsForDataTypes(preparedLists, listsToFree)

cdef evaluateList_UnknownType(Falloff falloff, dict preparedLists, Py_ssize_t startIndex,
                              Py_ssize_t amount, float *target):
    if isinstance(falloff, BaseFalloff):
        evaluateList_BaseFalloff(falloff, preparedLists, startIndex, amount, target)
    elif isinstance(falloff, CompoundFalloff):
        evaluateList_CompoundFalloff(falloff, preparedLists, startIndex, amount, target)

cdef evaluateList_BaseFalloff(BaseFalloff falloff, dict preparedLists, Py_ssize_t startIndex,
                              Py_ssize_t amount, float *target):
    cdef void *data = intToPointer(preparedLists[falloff.dataType])
    falloff.evaluateList(data, startIndex, amount, target)

cdef evaluateList_CompoundFalloff(CompoundFalloff falloff, dict preparedLists,
                                  Py_ssize_t startIndex, Py_ssize_t amount, float *target):
    cdef list dependencies = falloff.getDependencies()
    cdef list clampingRequirements = falloff.getClampingRequirements()
    cdef list subResults = evaluateList_UnkownType_Multiple(dependencies, preparedLists,
                                                            startIndex, amount)

    cdef Falloff subFalloff
    for subFalloff, subResult, clampRequired in zip(dependencies, subResults, clampingRequirements):
        if clampRequired and not subFalloff.clamped:
            subResult.clamp(0, 1)

    cdef float **depsResults = <float**>PyMem_Malloc(sizeof(float*) * len(dependencies))

    cdef Py_ssize_t i
    for i in range(len(dependencies)):
        depsResults[i] = (<FloatList>subResults[i]).data
    falloff.evaluateList(depsResults, amount, target)

    PyMem_Free(depsResults)

cdef evaluateList_UnkownType_Multiple(list falloffs, dict preparedLists,
                                      Py_ssize_t startIndex, Py_ssize_t amount):
    cdef list results = []
    cdef FloatList result
    for falloff in falloffs:
        result = FloatList(length = amount)
        evaluateList_UnknownType(falloff, preparedLists, startIndex, amount, result.data)
        results.append(result)
    return results

cdef set getBaseFalloffTypes(Falloff falloff):
    if isinstance(falloff, BaseFalloff):
        return {(<BaseFalloff>falloff).dataType}

    cdef list deps
    if isinstance(falloff, CompoundFalloff):
        deps = (<CompoundFalloff>falloff).getDependencies()
        return {t for d in deps for t in getBaseFalloffTypes(d)}

cdef getListsForDataTypes(str sourceType, set dataTypes, void *values, Py_ssize_t amount):
    cdef dict lists = {}
    cdef set listsToFree = set()
    cdef void *ptr
    for dataType in dataTypes:
        if typeConversionRequired(sourceType, dataType):
            elementSize = getSizeOfFalloffDataType(dataType)
            ptr = PyMem_Malloc(amount * elementSize)
            getConvertListFunction(sourceType, dataType)(values, ptr, amount)
            lists[dataType] = pointerToInt(ptr)
            listsToFree.add(dataType)
        else:
            lists[dataType] = pointerToInt(values)
    return lists, listsToFree

cdef freeListsForDataTypes(dict lists, set listsToFree):
    for dataType in listsToFree:
        PyMem_Free(intToPointer(lists[dataType]))
