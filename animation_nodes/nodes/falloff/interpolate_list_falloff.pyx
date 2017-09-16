from . constant_falloff import ConstantFalloff
from ... data_structures cimport (FloatList, Falloff, BaseFalloff,
                                  CompoundFalloff, Interpolation)

def createIndexBasedFalloff(str extensionMode, FloatList myList,
                float length, float offset, Interpolation interpolation):
    if len(myList) == 0:
        return ConstantFalloff(0)
    if len(myList) == 1 or length == 0:
        return ConstantFalloff(myList[0])

    if extensionMode == "LOOP":
        return Loop_InterpolateDoubleListFalloff(myList, length, offset, interpolation)
    elif extensionMode == "MIRROR":
        return Loop_InterpolateDoubleListFalloff(myList + myList.reversed(), length * 2, offset * 2, interpolation)
    elif extensionMode == "EXTEND":
        return Extend_InterpolateDoubleListFalloff(myList, length, offset, interpolation)
    else:
        raise Exception("invalid extension mode")

def createFalloffBasedFalloff(Falloff falloff, FloatList myList, Interpolation interpolation):
    if len(myList) == 0:
        return ConstantFalloff(0)
    if len(myList) == 1:
        return ConstantFalloff(myList[0])

    return Falloff_InterpolateDoubleListFalloff(falloff, myList, interpolation)

cdef float evaluatePosition(float x, FloatList myList, Interpolation interpolation):
    cdef Py_ssize_t indexBefore = <Py_ssize_t>x
    cdef float influence = interpolation.evaluate(x - <float>indexBefore)
    cdef Py_ssize_t indexAfter
    if indexBefore < myList.length - 1:
        indexAfter = indexBefore + 1
    else:
        indexAfter = indexBefore
    return myList.data[indexBefore] * (1 - influence) + myList.data[indexAfter] * influence

cdef class BaseInterpolateDoubleListFalloff(BaseFalloff):
    cdef:
        FloatList myList
        Interpolation interpolation
        float length, offset

    def __cinit__(self, FloatList myList, float length, float offset, Interpolation interpolation):
        self.myList = myList
        self.length = length
        self.offset = offset
        self.interpolation = interpolation
        self.dataType = "All"
        self.clamped = False

cdef class Loop_InterpolateDoubleListFalloff(BaseInterpolateDoubleListFalloff):
    cdef float evaluate(self, void *object, Py_ssize_t _index):
        cdef float index = (<float>_index + self.offset) % self.length
        cdef float x = index / (self.length - 1) * (self.myList.length - 1)
        return evaluatePosition(x, self.myList, self.interpolation)

cdef class Extend_InterpolateDoubleListFalloff(BaseInterpolateDoubleListFalloff):
    cdef float evaluate(self, void *object, Py_ssize_t _index):
        cdef float index = <float>_index + self.offset
        index = min(max(index, 0), self.length - 1)
        cdef float x = index / (self.length - 1) * (self.myList.length - 1)
        return evaluatePosition(x, self.myList, self.interpolation)


cdef class Falloff_InterpolateDoubleListFalloff(CompoundFalloff):
    cdef:
        Falloff falloff
        FloatList myList
        Interpolation interpolation

    def __cinit__(self, Falloff falloff, FloatList myList, Interpolation interpolation):
        self.falloff = falloff
        self.myList = myList
        self.interpolation = interpolation
        self.clamped = False

    cdef list getDependencies(self):
        return [self.falloff]

    cdef list getClampingRequirements(self):
        return [True]

    cdef float evaluate(self, float *dependencyResults):
        cdef float x = dependencyResults[0] * (self.myList.length - 1)
        return evaluatePosition(x, self.myList, self.interpolation)
