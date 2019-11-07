from .. lists.clist cimport CList
from . falloff_base cimport BaseFalloff

ctypedef object (*PyConversionFunction)(object value, void *target)
ctypedef float (*EvaluateBaseConverted)(BaseFalloff, void *value, Py_ssize_t index)
ctypedef void (*ConvertList)(void *source, void *target, Py_ssize_t amount)

cdef set getFalloffDataTypes()
cdef bint falloffDataTypeExists(str dataType)
cdef getSizeOfFalloffDataType(str dataType)
cdef typeConversionRequired(str sourceType, str dataType)
cdef EvaluateBaseConverted getCallConvertedFunction(str sourceType, str dataType)
cdef PyConversionFunction getPyConversionFunction(str dataType)
cdef ConvertList getConvertListFunction(str sourceType, str dataType)
cdef bint isValidSourceForDataTypes(str sourceType, dataTypes)
cdef bint isValidSourceForDataType(str sourceType, str dataType)
