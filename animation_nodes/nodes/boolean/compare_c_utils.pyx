from ... data_structures cimport DoubleList, BooleanList, LongList

def equal_DoubleList(DoubleList a, DoubleList b):
    cdef BooleanList result = BooleanList(length = a.length)
    cdef long i
    for i in range(a.length):
        result.data[i] = a.data[i] == b.data[i]
    return result

def notEqual_DoubleList(DoubleList a, DoubleList b):
    cdef BooleanList result = BooleanList(length = a.length)
    cdef long i
    for i in range(a.length):
        result.data[i] = a.data[i] != b.data[i]
    return result

def greater_DoubleList(DoubleList a, DoubleList b):
    cdef BooleanList result = BooleanList(length = a.length)
    cdef long i
    for i in range(a.length):
        result.data[i] = a.data[i] > b.data[i]
    return result

def greaterEqual_DoubleList(DoubleList a, DoubleList b):
    cdef BooleanList result = BooleanList(length = a.length)
    cdef long i
    for i in range(a.length):
        result.data[i] = a.data[i] >= b.data[i]
    return result

def less_DoubleList(DoubleList a, DoubleList b):
    cdef BooleanList result = BooleanList(length = a.length)
    cdef long i
    for i in range(a.length):
        result.data[i] = a.data[i] < b.data[i]
    return result

def lessEqual_DoubleList(DoubleList a, DoubleList b):
    cdef BooleanList result = BooleanList(length = a.length)
    cdef long i
    for i in range(a.length):
        result.data[i] = a.data[i] <= b.data[i]
    return result

def equal_LongList(LongList a, LongList b):
    cdef BooleanList result = BooleanList(length = a.length)
    cdef long i
    for i in range(a.length):
        result.data[i] = a.data[i] == b.data[i]
    return result

def notEqual_LongList(LongList a, LongList b):
    cdef BooleanList result = BooleanList(length = a.length)
    cdef long i
    for i in range(a.length):
        result.data[i] = a.data[i] != b.data[i]
    return result

def greater_LongList(LongList a, LongList b):
    cdef BooleanList result = BooleanList(length = a.length)
    cdef long i
    for i in range(a.length):
        result.data[i] = a.data[i] > b.data[i]
    return result

def greaterEqual_LongList(LongList a, LongList b):
    cdef BooleanList result = BooleanList(length = a.length)
    cdef long i
    for i in range(a.length):
        result.data[i] = a.data[i] >= b.data[i]
    return result

def less_LongList(LongList a, LongList b):
    cdef BooleanList result = BooleanList(length = a.length)
    cdef long i
    for i in range(a.length):
        result.data[i] = a.data[i] < b.data[i]
    return result

def lessEqual_LongList(LongList a, LongList b):
    cdef BooleanList result = BooleanList(length = a.length)
    cdef long i
    for i in range(a.length):
        result.data[i] = a.data[i] <= b.data[i]
    return result
