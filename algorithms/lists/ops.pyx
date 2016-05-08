from ... data_structures.lists.base_lists cimport numeric_list, UShortList

def repeatList(numeric_list source, long finalLength):
    if len(source) == 0:
        raise ValueError("Length of the source list has to be >0")
    finalLength = max(0, finalLength)
    cdef UShortList newList = UShortList(finalLength)
    cdef long i = 0
    cdef long k = 0
    while(i < finalLength):
        newList.data[i] = <unsigned short>source.data[k]
        i += 1
        k += 1
        if k == source.length:
            k = 0
    return newList
