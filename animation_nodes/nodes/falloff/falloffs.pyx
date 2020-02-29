from ... math cimport Vector3
from ... data_structures cimport (
    FalloffEvaluator, Vector3DList, FloatList,
    VirtualVector3DList, VirtualDoubleList, VirtualFloatList
)

def offsetFloatList(Vector3DList vectors, FloatList numbers, VirtualDoubleList offsets, FalloffEvaluator falloffEvaluator, bint invert = False):
    cdef FloatList influences = falloffEvaluator.evaluateList(vectors)

    cdef float influence
    cdef double offset
    cdef Py_ssize_t i

    for i in range(len(numbers)):
        influence = influences.data[i]

        if invert:
            influence = <float>1 - influence

        offset = offsets.get(i)
        numbers.data[i] += offset * influence

def offsetVector3DList(Vector3DList vectors, VirtualVector3DList offsets, VirtualFloatList influences, bint invert = False):
    cdef Vector3 *offset
    cdef float influence
    cdef Py_ssize_t i

    for i in range(len(vectors)):
        influence = influences.get(i)

        if invert:
            influence = <float>1 - influence

        offset = offsets.get(i)
        vectors.data[i].x += offset.x * influence
        vectors.data[i].y += offset.y * influence
        vectors.data[i].z += offset.z * influence
