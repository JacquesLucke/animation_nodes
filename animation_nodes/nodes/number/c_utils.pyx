from ... data_structures cimport (
    LongList,
    FloatList,
    DoubleList,
    BooleanList,
    Interpolation,
    VirtualDoubleList
)

from ... utils.limits cimport INT_MAX
from ... utils.clamp cimport clamp, clampLong
from ... algorithms.random cimport randomDouble_Range
from ... math cimport degreeToRadian, radianToDegree

def range_LongList_StartStep(amount, start, step):
    cdef long long _amount = clampLong(amount)
    cdef long long _start = clampLong(start)
    cdef long long _step = clampLong(step)

    cdef LongList newList = LongList(length = max(_amount, 0))
    cdef Py_ssize_t i
    for i in range(len(newList)):
        newList.data[i] = _start + i * _step
    return newList

def range_DoubleList_StartStep(amount, double start, double step):
    cdef DoubleList newList
    cdef Py_ssize_t i
    if step == 0:
        newList = DoubleList.fromValues([start]) * amount
    else:
        newList = DoubleList(length = amount)
        for i in range(len(newList)):
            newList.data[i] = start + i * step
    return newList

def range_DoubleList_StartStep_Interpolated(amount, double start,
        double step, Interpolation interpolation):
    cdef DoubleList newList
    cdef double stop
    cdef double unityStep
    cdef Py_ssize_t i
    if step == 0:
        newList = DoubleList.fromValues([start]) * amount
    else:
        newList = DoubleList(length = amount)
        unityStep = 1.0 / (amount - 1)
        stop = step * (amount - 1)
        for i in range(amount):
            newList.data[i] = start + interpolation.evaluate(i * unityStep) * stop
    return newList

def random_DoubleList(seed, amount, double minValue, double maxValue):
    cdef DoubleList newList = DoubleList(length = max(0, amount))
    cdef int _seed = (seed * 234235) % INT_MAX
    cdef Py_ssize_t i

    for i in range(len(newList)):
        newList.data[i] = randomDouble_Range(_seed + i, minValue, maxValue)
    return newList

def mapRange_DoubleList(DoubleList values, bint clamped,
                        double inMin, double inMax,
                        double outMin, double outMax):
    if inMin == inMax:
        return DoubleList.fromValues([0]) * len(values)

    cdef:
        DoubleList newValues = DoubleList(length = len(values))
        double factor = (outMax - outMin) / (inMax - inMin)
        double x
        long i

    for i in range(len(newValues)):
        x = values.data[i]
        if clamped: x = clamp(x, inMin, inMax) if inMin < inMax else clamp(x, inMax, inMin)
        newValues.data[i] = outMin + (x - inMin) * factor

    return newValues

def mapRange_DoubleList_Interpolated(DoubleList values, Interpolation interpolation,
                                     double inMin, double inMax,
                                     double outMin, double outMax):
     if inMin == inMax:
         return DoubleList.fromValues([0]) * values.length

     cdef:
         DoubleList newValues = DoubleList(length = len(values))
         double factor1 = 1 / (inMax - inMin)
         double factor2 = outMax - outMin
         double x
         long i

     for i in range(len(newValues)):
         x = clamp(values.data[i], inMin, inMax) if inMin < inMax else clamp(values.data[i], inMax, inMin)
         newValues.data[i] = outMin + interpolation.evaluate((x - inMin) * factor1) * factor2

     return newValues

def offsetFloats(FloatList numbers, VirtualDoubleList offsets, FloatList influences):
    cdef double offset
    cdef Py_ssize_t i

    for i in range(len(numbers)):
        offset = offsets.get(i)
        numbers.data[i] += offset * influences.data[i]

def compareNumbers_Equal(VirtualDoubleList a, VirtualDoubleList b, long amount):
    cdef BooleanList result = BooleanList(length = amount)
    cdef Py_ssize_t i
    for i in range(amount):
        result.data[i] = a.get(i) == b.get(i)
    return result

def compareNumbers_NotEqual(VirtualDoubleList a, VirtualDoubleList b, long amount):
    cdef BooleanList result = BooleanList(length = amount)
    cdef Py_ssize_t i
    for i in range(amount):
        result.data[i] = a.get(i) != b.get(i)
    return result

def compareNumbers_LessThan(VirtualDoubleList a, VirtualDoubleList b, long amount):
    cdef BooleanList result = BooleanList(length = amount)
    cdef Py_ssize_t i
    for i in range(amount):
        result.data[i] = a.get(i) < b.get(i)
    return result

def compareNumbers_GreaterThan(VirtualDoubleList a, VirtualDoubleList b, long amount):
    cdef BooleanList result = BooleanList(length = amount)
    cdef Py_ssize_t i
    for i in range(amount):
        result.data[i] = a.get(i) > b.get(i)
    return result

def compareNumbers_LessThanOrEqual(VirtualDoubleList a, VirtualDoubleList b, long amount):
    cdef BooleanList result = BooleanList(length = amount)
    cdef Py_ssize_t i
    for i in range(amount):
        result.data[i] = a.get(i) <= b.get(i)
    return result

def compareNumbers_GreaterThanOrEqual(VirtualDoubleList a, VirtualDoubleList b, long amount):
    cdef BooleanList result = BooleanList(length = amount)
    cdef Py_ssize_t i
    for i in range(amount):
        result.data[i] = a.get(i) >= b.get(i)
    return result

def degreesToRadians(DoubleList values):
    cdef Py_ssize_t i
    cdef Py_ssize_t amount = values.length
    cdef DoubleList result = DoubleList(length = amount)
    for i in range(amount):
        result.data[i] = degreeToRadian(values.data[i])
    return result

def radiansToDegrees(DoubleList values):
    cdef Py_ssize_t i
    cdef Py_ssize_t amount = values.length
    cdef DoubleList result = DoubleList(length = amount)
    for i in range(amount):
        result.data[i] = radianToDegree(values.data[i])
    return result
