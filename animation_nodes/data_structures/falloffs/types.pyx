from libc.stdint cimport intptr_t
from ... math cimport Vector3, Matrix4, setVector3, setMatrix4


# Public Interface
############################################################

cdef set getFalloffDataTypes():
    return dataTypes

cdef bint falloffDataTypeExists(str dataType):
    return dataType in dataTypes

cdef getSizeOfFalloffDataType(str dataType):
    return cSizePerDataType[dataType]

cdef typeConversionRequired(str sourceType, str dataType):
    return (sourceType, dataType) not in noConversionRequired

cdef EvaluateBaseConverted getCallConvertedFunction(str sourceType, str dataType):
    return <EvaluateBaseConverted><intptr_t>conversions.get((sourceType, dataType), 0)

cdef PyConversionFunction getPyConversionFunction(str dataType):
    return <PyConversionFunction><intptr_t>pyConversionPerDataType.get(dataType, 0)

cdef bint isValidSourceForDataTypes(str sourceType, dataTypes):
    cdef str dataType
    for dataType in dataTypes:
        if not isValidSourceForDataType(sourceType, dataType):
            return False
    return True

cdef bint isValidSourceForDataType(str sourceType, str dataType):
    return (sourceType, dataType) in noConversionRequired or (sourceType, dataType) in conversions


# Data structure for public interface
############################################################

cdef set dataTypes = set()
cdef dict cSizePerDataType = dict()
cdef dict conversions = dict()
cdef set noConversionRequired = set()
cdef dict pyConversionPerDataType = dict()

cdef initializeFalloffDataTypes():
    dataTypes.add("None")
    cSizePerDataType["None"] = 0
    noConversionRequired.add(("None", "None"))
    pyConversionPerDataType["None"] = <intptr_t>pyToNone

cdef registerFalloffDataType(str identifier, Py_ssize_t cSize, PyConversionFunction pyConversion):
    dataTypes.add(identifier)
    cSizePerDataType[identifier] = cSize
    noConversionRequired.add((identifier, "None"))
    noConversionRequired.add((identifier, identifier))
    pyConversionPerDataType[identifier] = <intptr_t>pyConversion

cdef registerConversion(str source, str target, EvaluateBaseConverted callConverted):
    conversions[(source, target)] = <intptr_t>callConverted



# Create default types
############################################################

initializeFalloffDataTypes()

registerFalloffDataType(
    identifier = "Location",
    cSize = sizeof(Vector3),
    pyConversion = pyToLocation
)

registerFalloffDataType(
    identifier = "Transformation Matrix",
    cSize = sizeof(Matrix4),
    pyConversion = pyToTransformationMatrix
)

registerConversion("Transformation Matrix", "Location",
    callConverted = callConverted_TransformationMatrix_Location)

# Internals
##################################################################

cdef float callConverted_TransformationMatrix_Location(BaseFalloff falloff,
                                                       void *value, Py_ssize_t index):
    cdef Matrix4 *m = <Matrix4*>value
    cdef Vector3 v
    v.x, v.y, v.z = m.a14, m.a24, m.a34
    return falloff.evaluate(&v, index)

cdef pyToLocation(object source, void *v):
    setVector3(<Vector3*>v, source)

cdef pyToTransformationMatrix(object source, void *m):
    setMatrix4(<Matrix4*>m, source)

cdef pyToNone(object source, void *target):
    pass
