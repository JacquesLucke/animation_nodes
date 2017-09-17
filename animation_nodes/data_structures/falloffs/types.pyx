from libc.stdint cimport intptr_t
from ... math cimport Vector3, Matrix4, setVector3, setMatrix4

cdef class FalloffSourceType:
    def __cinit__(self, str identifier, Py_ssize_t cSize):
        self.identifier = identifier
        self.cSize = cSize
        self.callConvertedFunctions = {}
        self.pyConversion = NULL

    cdef setPyConversion(self, PyConversionFunction pyConversion):
        self.pyConversion = pyConversion

    cdef addConvertedCall(self, str sourceType, EvaluateBaseConverted function):
        self.callConvertedFunctions[sourceType] = <intptr_t>function

    cdef EvaluateBaseConverted getConvertedCall(self, str sourceType):
        return (<EvaluateBaseConverted><intptr_t>
                self.callConvertedFunctions.get(sourceType, 0))


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


cdef FalloffSourceType none, location, transformationMatrix
none = FalloffSourceType("None", 0)
location = FalloffSourceType("Location", sizeof(Vector3))
transformationMatrix = FalloffSourceType("Transformation Matrix", sizeof(Matrix4))

none.setPyConversion(pyToNone)
location.setPyConversion(pyToLocation)
transformationMatrix.setPyConversion(pyToTransformationMatrix)

location.addConvertedCall(transformationMatrix.identifier,
    callConverted_TransformationMatrix_Location)

cdef dict sourceTypes = {
    none.identifier : none,
    location.identifier : location,
    transformationMatrix.identifier : transformationMatrix
}

cdef dict getFalloffSourceTypes():
    return sourceTypes

cdef FalloffSourceType getFalloffSourceType(str sourceType):
    return sourceTypes[sourceType]

cdef sourceTypeExists(str sourceType):
    return sourceType in sourceTypes
