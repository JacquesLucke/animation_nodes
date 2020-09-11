from ... data_structures cimport DoubleList, BooleanList, LongList
from ... algorithms.random_number_generators cimport XoShiRo256StarStar

def convert_DoubleList_to_BooleanList(DoubleList inList):
    cdef BooleanList outList = BooleanList(length = inList.length)
    cdef long i
    for i in range(len(inList)):
        outList.data[i] = inList.data[i] != 0
    return outList

def convert_LongList_to_BooleanList(LongList inList):
    cdef BooleanList outList = BooleanList(length = inList.length)
    cdef long i
    for i in range(len(inList)):
        outList.data[i] = inList.data[i] != 0
    return outList

def convert_BooleanList_to_LongList(BooleanList inList):
    cdef LongList outList = LongList(length = inList.length)
    cdef long i
    for i in range(len(inList)):
        outList.data[i] = 1 if inList.data[i] != 0 else 0
    return outList

def convert_BooleanList_to_DoubleList(BooleanList inList):
    cdef DoubleList outList = DoubleList(length = inList.length)
    cdef long i
    for i in range(len(inList)):
        outList.data[i] = 1 if inList.data[i] != 0 else 0
    return outList

def generateRandomBooleans(Py_ssize_t count, Py_ssize_t seed):
    cdef Py_ssize_t i
    cdef XoShiRo256StarStar rng = XoShiRo256StarStar(seed)
    cdef BooleanList bools = BooleanList(length = count)
    for i in range(count):
        bools.data[i] = rng.nextBoolean()
    return bools
