cimport cython
from ... math cimport Vector3, Euler3, Quaternion, Matrix4
from ... data_structures cimport (
    Color,
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
    VirtualMatrix4x4List,
)

def mixDoubleLists(VirtualDoubleList numbersA, VirtualDoubleList numbersB, VirtualDoubleList factors):
    cdef long amount = VirtualDoubleList.getMaxRealLength(numbersA, numbersB, factors)
    cdef DoubleList results = DoubleList(length = amount)
    cdef Py_ssize_t i

    for i in range(amount):
        results.data[i] = lerp(<float>numbersA.get(i), <float>numbersB.get(i), <float>factors.get(i))

    return results

def mixVectorLists(VirtualVector3DList vectorsA, VirtualVector3DList vectorsB, VirtualDoubleList factors):
    cdef long amount = VirtualDoubleList.getMaxRealLength(vectorsA, vectorsB, factors)
    cdef Vector3DList results = Vector3DList(length = amount)
    cdef Vector3 *vectorA
    cdef Vector3 *vectorB
    cdef float factor
    cdef Py_ssize_t i

    for i in range(amount):
        factor = <float>factors.get(i)
        vectorA = vectorsA.get(i)
        vectorB = vectorsB.get(i)
        results.data[i].x = lerp(vectorA.x, vectorB.x, factor)
        results.data[i].y = lerp(vectorA.y, vectorB.y, factor)
        results.data[i].z = lerp(vectorA.x, vectorB.z, factor)

    return results

def mixQuaternionLists(QuaternionList quaternionsA, QuaternionList quaternionsB, VirtualDoubleList factors):
    cdef long amount = factors.getRealLength()
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
        factor = <float>factors.get(i)
        quaternionA = _quaternionsA.data[i]
        quaternionB = _quaternionsB.data[i]
        results.data[i].w = lerp(quaternionA.w, quaternionB.w, factor)
        results.data[i].x = lerp(quaternionA.x, quaternionB.x, factor)
        results.data[i].y = lerp(quaternionA.y, quaternionB.y, factor)
        results.data[i].z = lerp(quaternionA.z, quaternionB.z, factor)

    return results

def mixMatrixLists(VirtualMatrix4x4List matricesA, VirtualMatrix4x4List matricesB, VirtualDoubleList factors):
    cdef long amount = VirtualDoubleList.getMaxRealLength(matricesA, matricesB, factors)
    cdef Matrix4x4List results = Matrix4x4List(length = amount)
    cdef Py_ssize_t i

    for i in range(amount):
        mixMatrices(results.data + i, matricesA.get(i), matricesB.get(i), <float>factors.get(i))

    return results

def mixColorLists(VirtualColorList colorsA, VirtualColorList colorsB, VirtualDoubleList factors):
    cdef long amount = VirtualDoubleList.getMaxRealLength(colorsA, colorsB, factors)
    cdef ColorList results = ColorList(length = amount)
    cdef Color *colorA
    cdef Color *colorB
    cdef float factor
    cdef Py_ssize_t i

    for i in range(amount):
        factor = <float>factors.get(i)
        colorA = colorsA.get(i)
        colorB = colorsB.get(i)
        results.data[i].r = lerp(colorA.r, colorB.r, factor)
        results.data[i].g = lerp(colorA.g, colorB.g, factor)
        results.data[i].b = lerp(colorA.b, colorB.b, factor)
        results.data[i].a = lerp(colorA.a, colorB.a, factor)

    return results

def mixEulerLists(VirtualEulerList eulersA, VirtualEulerList eulersB, VirtualDoubleList factors):
    cdef long amount = VirtualDoubleList.getMaxRealLength(eulersA, eulersB, factors)
    cdef EulerList results = EulerList(length = amount)
    cdef Euler3 *eulerA
    cdef Euler3 *eulerB
    cdef float factor
    cdef Py_ssize_t i

    results.fill(0)
    for i in range(amount):
        factor = <float>factors.get(i)
        eulerA = eulersA.get(i)
        eulerB = eulersB.get(i)
        results.data[i].x = lerp(eulerA.x, eulerB.x, factor)
        results.data[i].y = lerp(eulerA.y, eulerB.y, factor)
        results.data[i].z = lerp(eulerA.z, eulerB.z, factor)

    return results

cdef mixMatrices(Matrix4* target, Matrix4* x, Matrix4* y, float factor):
    target.a11 = lerp(x.a11, y.a11, factor)
    target.a12 = lerp(x.a12, y.a12, factor)
    target.a13 = lerp(x.a13, y.a13, factor)
    target.a14 = lerp(x.a14, y.a14, factor)

    target.a21 = lerp(x.a21, y.a21, factor)
    target.a22 = lerp(x.a22, y.a22, factor)
    target.a23 = lerp(x.a23, y.a23, factor)
    target.a24 = lerp(x.a24, y.a24, factor)

    target.a31 = lerp(x.a31, y.a31, factor)
    target.a32 = lerp(x.a32, y.a32, factor)
    target.a33 = lerp(x.a33, y.a33, factor)
    target.a34 = lerp(x.a34, y.a34, factor)

    target.a41 = lerp(x.a41, y.a41, factor)
    target.a42 = lerp(x.a42, y.a42, factor)
    target.a43 = lerp(x.a43, y.a43, factor)
    target.a44 = lerp(x.a44, y.a44, factor)

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
