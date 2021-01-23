from ... math cimport lerp, mixVec3, mixEul3, mixQuat, mixColor
from ... data_structures cimport (
    ColorList,
    EulerList,
    DoubleList,
    Vector3DList,
    QuaternionList,
    Interpolation,
    VirtualColorList,
    VirtualEulerList,
    VirtualDoubleList,
    VirtualVector3DList,
    VirtualQuaternionList,
)

def mixDoubleLists(VirtualDoubleList numbersA, VirtualDoubleList numbersB, VirtualDoubleList factors,
                   long amount):
    cdef DoubleList results = DoubleList(length = amount)
    cdef Py_ssize_t i

    for i in range(amount):
        results.data[i] = lerp(numbersA.get(i), numbersB.get(i), factors.get(i))

    return results

def mixVectorLists(VirtualVector3DList vectorsA, VirtualVector3DList vectorsB, VirtualDoubleList factors,
                   long amount):
    cdef Vector3DList results = Vector3DList(length = amount)
    cdef Py_ssize_t i

    for i in range(amount):
        mixVec3(results.data + i, vectorsA.get(i), vectorsB.get(i), <float>factors.get(i))

    return results

def mixQuaternionLists(VirtualQuaternionList quaternionsA, VirtualQuaternionList quaternionsB, VirtualDoubleList factors,
                       long amount):
    cdef QuaternionList results = QuaternionList(length = amount)
    cdef Py_ssize_t i

    for i in range(amount):
        mixQuat(results.data + i, quaternionsA.get(i), quaternionsB.get(i), <float>factors.get(i))

    return results

def mixColorLists(VirtualColorList colorsA, VirtualColorList colorsB, VirtualDoubleList factors,
                  long amount):
    cdef ColorList results = ColorList(length = amount)
    cdef Py_ssize_t i

    for i in range(amount):
        mixColor(results.data + i, colorsA.get(i), colorsB.get(i), <float>factors.get(i))

    return results

def mixEulerLists(VirtualEulerList eulersA, VirtualEulerList eulersB, VirtualDoubleList factors,
                  long amount):
    cdef EulerList results = EulerList(length = amount)
    cdef Py_ssize_t i

    for i in range(amount):
        mixEul3(results.data + i, eulersA.get(i), eulersB.get(i), <float>factors.get(i))

    return results

def calculateInfluenceList(VirtualDoubleList times,
                        Interpolation interpolation,
                        VirtualDoubleList durations, long amount):
    cdef DoubleList result = DoubleList(length = amount)
    cdef Py_ssize_t i
    for i in range(amount):
        finalDuration = max(durations.get(i), 0.0001)
        influence = max(min(times.get(i) / finalDuration, 1.0), 0.0)
        result.data[i] = interpolation.evaluate(influence)
    return result

def executeTimeList(VirtualDoubleList times, VirtualDoubleList durations, long amount):
    cdef DoubleList result = DoubleList(length = amount)
    cdef Py_ssize_t i
    for i in range(amount):
        finalDuration = max(durations.get(i), 0.0001)
        result.data[i] = times.get(i) - finalDuration
    return result

