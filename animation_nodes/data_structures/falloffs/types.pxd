from . falloff_base cimport BaseFalloff

ctypedef object (*PyConversionFunction)(object source, void *target)
ctypedef float (*EvaluateBaseConverted)(BaseFalloff, void *value, Py_ssize_t index)

cdef dict getFalloffSourceTypes()
cdef FalloffSourceType getFalloffSourceType(str sourceType)
cdef sourceTypeExists(str sourceType)

cdef class FalloffSourceType:
    cdef str identifier
    cdef Py_ssize_t cSize
    cdef dict conversions
    cdef dict callConvertedFunctions

    cdef PyConversionFunction pyConversion

    cdef setPyConversion(self, PyConversionFunction pyConversion)

    cdef addConvertedCall(self, str sourceType, EvaluateBaseConverted function)
    cdef EvaluateBaseConverted getConvertedCall(self, str sourceType)
