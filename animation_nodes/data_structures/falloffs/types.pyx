from ... utils.pointers cimport intToPointer, pointerToInt

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
    return <EvaluateBaseConverted>intToPointer(conversions.get((sourceType, dataType), 0))

cdef PyConversionFunction getPyConversionFunction(str dataType):
    return <PyConversionFunction>intToPointer(pyConversionPerDataType.get(dataType, 0))

cdef ConvertList getConvertListFunction(str sourceType, str dataType):
    return <ConvertList>intToPointer(convertListFunctions.get((sourceType, dataType), 0))

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
cdef dict convertListFunctions = dict()

cdef initializeFalloffDataTypes():
    dataTypes.add("None")
    cSizePerDataType["None"] = 0
    noConversionRequired.add(("None", "None"))
    pyConversionPerDataType["None"] = pointerToInt(<void*>pyToNone)

cdef registerFalloffDataType(str identifier, Py_ssize_t cSize, PyConversionFunction pyConversion):
    dataTypes.add(identifier)
    cSizePerDataType[identifier] = cSize
    noConversionRequired.add((identifier, "None"))
    noConversionRequired.add((identifier, identifier))
    pyConversionPerDataType[identifier] = pointerToInt(<void*>pyConversion)

cdef registerConversion(str source, str target,
                        EvaluateBaseConverted callConverted, ConvertList convertList):
    conversions[(source, target)] = pointerToInt(<void*>callConverted)
    convertListFunctions[(source, target)] = pointerToInt(<void*>convertList)


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
    callConverted = callConverted_TransformationMatrix_Location,
    convertList = convertList_TransformationMatrix_Location
)


# Actual types
##################################################################

from .. lists.base_lists cimport Vector3DList, Matrix4x4List
from ... math cimport Vector3, Matrix4, setVector3, setMatrix4

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

cdef void convertList_TransformationMatrix_Location(void *source, void *target, Py_ssize_t amount):
    cdef Matrix4 *matrices = <Matrix4*>source
    cdef Vector3 *vectors = <Vector3*>target
    for i in range(amount):
        vectors[i].x = matrices[i].a14
        vectors[i].y = matrices[i].a24
        vectors[i].z = matrices[i].a34
