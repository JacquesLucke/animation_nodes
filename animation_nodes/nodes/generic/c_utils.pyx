cimport cython
from ... math cimport Vector3, Quaternion
from ... data_structures cimport (
    FloatList, VirtualFloatList, Vector3DList, VirtualVector3DList, QuaternionList)

def mixFloatLists(VirtualFloatList numbersA, VirtualFloatList numbersB, FloatList influences):
    cdef long amount = influences.length
    cdef FloatList results = FloatList(length = amount)
    cdef Py_ssize_t i

    for i in range(amount):
        results.data[i].x = lerp(numbersA.get(i), numbersB.get(i), influences.data[i])

    return results

def mixVectorLists(VirtualVector3DList vectorsA, VirtualVector3DList vectorsB, FloatList influences):
    cdef long amount = influences.length
    cdef Vector3DList results = Vector3DList(length = amount)
    cdef Vector3 *vectorA
    cdef Vector3 *vectorB
    cdef float influence
    cdef Py_ssize_t i

    for i in range(amount):
        vectorA = vectorsA.get(i)
        vectorB = vectorsB.get(i)
        influence = influences.data[i]
        results.data[i].x = lerp(vectorA.x, vectorB.x, influence)
        results.data[i].y = lerp(vectorA.y, vectorB.y, influence)
        results.data[i].z = lerp(vectorA.x, vectorB.z, influence)

    return results

def mixQuaternionLists(QuaternionList quaternionsA, QuaternionList quaternionsB, FloatList influences):
    cdef long amount = influences.length
    cdef QuaternionList results = QuaternionList(length = amount)
    cdef Quaternion quaternionA
    cdef Quaternion quaternionB
    cdef float influence
    cdef Py_ssize_t i

    for i in range(amount):
        quaternionA = quaternionsA.data[i]
        quaternionB = quaternionsB.data[i]
        influence = influences.data[i]
        results.data[i].x = lerp(quaternionA.x, quaternionB.x, influence)
        results.data[i].y = lerp(quaternionA.y, quaternionB.y, influence)
        results.data[i].z = lerp(quaternionA.z, quaternionB.z, influence)
        results.data[i].w = lerp(quaternionA.w, quaternionB.w, influence)

    return results

cdef float lerp(float x, float y, float p):
    return (1.0 - p) * x + p * y
