from ... data_structures cimport (
    DoubleList
)

def clampDoubleList(DoubleList values, double minValue, double maxValue):
    cdef Py_ssize_t i
    for i in range(len(values)):
        if values.data[i] < minValue:
            values.data[i] = minValue
        elif values.data[i] > maxValue:
            values.data[i] = maxValue
