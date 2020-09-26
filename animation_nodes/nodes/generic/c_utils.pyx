cimport cython
from ... math cimport Vector3, Quaternion
from ... data_structures cimport (
    Color,
    ColorList,
    DoubleList,
    Vector3DList,
    QuaternionList,
    VirtualColorList,
    VirtualDoubleList,
    VirtualVector3DList
)

def mixDoubleLists(VirtualDoubleList numbersA, VirtualDoubleList numbersB, VirtualDoubleList influences):
    cdef long amount = VirtualDoubleList.getMaxRealLength(numbersA, numbersB, influences)
    cdef DoubleList results = DoubleList(length = amount)
    cdef Py_ssize_t i

    for i in range(amount):
        results.data[i] = lerp(numbersA.get(i), numbersB.get(i), influences.get(i))

    return results

def mixVectorLists(VirtualVector3DList vectorsA, VirtualVector3DList vectorsB, VirtualDoubleList influences):
    cdef long amount = VirtualDoubleList.getMaxRealLength(vectorsA, vectorsB, influences)
    cdef Vector3DList results = Vector3DList(length = amount)
    cdef Vector3 *vectorA
    cdef Vector3 *vectorB
    cdef float influence
    cdef Py_ssize_t i

    for i in range(amount):
        vectorA = vectorsA.get(i)
        vectorB = vectorsB.get(i)
        influence = influences.get(i)
        results.data[i].x = lerp(vectorA.x, vectorB.x, influence)
        results.data[i].y = lerp(vectorA.y, vectorB.y, influence)
        results.data[i].z = lerp(vectorA.x, vectorB.z, influence)

    return results

def mixQuaternionLists(QuaternionList quaternionsA, QuaternionList quaternionsB, VirtualDoubleList influences):
    cdef long amount = influences.getRealLength()
    cdef long amountA = quaternionsA.length
    cdef long amountB = quaternionsB.length
    amount = max(amount, amountA, amountB)

    cdef QuaternionList _quaternionsA = getVirtualQuaternionList(amount, quaternionsA)
    cdef QuaternionList _quaternionsB = getVirtualQuaternionList(amount, quaternionsB)
    cdef QuaternionList results = QuaternionList(length = amount)
    cdef Quaternion quaternionA
    cdef Quaternion quaternionB
    cdef float influence
    cdef Py_ssize_t i

    for i in range(amount):
        quaternionA = _quaternionsA.data[i]
        quaternionB = _quaternionsB.data[i]
        influence = influences.get(i)
        results.data[i].w = lerp(quaternionA.w, quaternionB.w, influence)
        results.data[i].x = lerp(quaternionA.x, quaternionB.x, influence)
        results.data[i].y = lerp(quaternionA.y, quaternionB.y, influence)
        results.data[i].z = lerp(quaternionA.z, quaternionB.z, influence)

    return results

def mixColorLists(VirtualColorList colorsA, VirtualColorList colorsB, VirtualDoubleList influences):
    cdef long amount = VirtualDoubleList.getMaxRealLength(colorsA, colorsB, influences)
    cdef ColorList results = ColorList(length = amount)
    cdef Color *colorA
    cdef Color *colorB
    cdef float influence
    cdef Py_ssize_t i

    for i in range(amount):
        influence = influences.get(i)
        colorA = colorsA.get(i)
        colorB = colorsB.get(i)
        results.data[i].r = lerp(colorA.r, colorB.r, influence)
        results.data[i].g = lerp(colorA.g, colorB.g, influence)
        results.data[i].b = lerp(colorA.b, colorB.b, influence)
        results.data[i].a = lerp(colorA.a, colorB.a, influence)

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

cdef float lerp(float x, float y, float p):
    return (1.0 - p) * x + p * y
