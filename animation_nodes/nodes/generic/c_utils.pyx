cimport cython
from ... math cimport lerp, Quaternion, mixVec3, mixEul3, mixMat4, mixQuat, mixColor
from ... data_structures cimport (
    ColorList,
    EulerList,
    DoubleList,
    Vector3DList,
    Matrix4x4List,
    QuaternionList,
    VirtualColorList,
    VirtualEulerList,
    VirtualDoubleList,
    VirtualVector3DList,
    VirtualMatrix4x4List
)

def mixDoubleLists(VirtualDoubleList numbersA, VirtualDoubleList numbersB, VirtualDoubleList factors,
                   long amount):
    cdef DoubleList results = DoubleList(length = amount)
    cdef Py_ssize_t i

    for i in range(amount):
        results.data[i] = lerp(<float>numbersA.get(i), <float>numbersB.get(i), <float>factors.get(i))

    return results

def mixVectorLists(VirtualVector3DList vectorsA, VirtualVector3DList vectorsB, VirtualDoubleList factors,
                   long amount):
    cdef Vector3DList results = Vector3DList(length = amount)
    cdef Py_ssize_t i

    for i in range(amount):
        mixVec3(results.data + i, vectorsA.get(i), vectorsB.get(i), <float>factors.get(i))

    return results

def mixQuaternionLists(QuaternionList quaternionsA, QuaternionList quaternionsB, VirtualDoubleList factors,
                       long amount):
    cdef long amountA = quaternionsA.length
    cdef long amountB = quaternionsB.length
    amount = max(amount, amountA, amountB)

    cdef QuaternionList _quaternionsA = getVirtualQuaternionList(amount, quaternionsA)
    cdef QuaternionList _quaternionsB = getVirtualQuaternionList(amount, quaternionsB)
    cdef QuaternionList results = QuaternionList(length = amount)
    cdef Quaternion quaternionA
    cdef Quaternion quaternionB
    cdef float factor
    cdef Py_ssize_t i

    for i in range(amount):
        mixQuat(results.data + i, _quaternionsA.data + i, _quaternionsB.data + i, <float>factors.get(i))

    return results

def mixMatrixLists(VirtualMatrix4x4List matricesA, VirtualMatrix4x4List matricesB, VirtualDoubleList factors,
                   long amount):
    cdef Matrix4x4List results = Matrix4x4List(length = amount)
    cdef Py_ssize_t i

    for i in range(amount):
        mixMat4(results.data + i, matricesA.get(i), matricesB.get(i), <float>factors.get(i))

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

    results.fill(0)
    for i in range(amount):
        mixEul3(results.data + i, eulersA.get(i), eulersB.get(i), <float>factors.get(i))

    return results

@cython.cdivision(True)
cdef QuaternionList getVirtualQuaternionList(long amount, QuaternionList qs):
    cdef long amountQ = qs.length
    if amountQ == amount: return qs

    cdef QuaternionList _qs = QuaternionList(length = amount)
    cdef Py_ssize_t i, index
    for i in range(amount):
        index = i
        if i >= amountQ:
            index = i % amountQ
        _qs.data[i] = qs.data[index]
    return _qs
