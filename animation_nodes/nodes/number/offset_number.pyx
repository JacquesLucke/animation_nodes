from ... data_structures cimport Falloff, FalloffEvaluator, FloatList, VirtualDoubleList, Vector3DList

def offsetFloatList(Vector3DList vectors, FloatList points, VirtualDoubleList offsets, FalloffEvaluator falloffEvaluator, bint invert = False):
    cdef FloatList influences = falloffEvaluator.evaluateList(vectors)

    cdef float influence
    cdef Py_ssize_t i

    for i in range(len(points)):
        influence = influences.data[i]

        if invert:
            influence = <float>1 - influence

        offset = offsets.get(i)
        points.data[i] += offset * influence
