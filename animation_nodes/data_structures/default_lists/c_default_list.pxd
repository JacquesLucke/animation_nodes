from . default_list cimport DefaultList
from .. lists.clist cimport CList

cdef class CDefaultList(DefaultList):
    cdef:
        object dataType
        CList realList
        CList defaultElementList

        char* arrayStart
        void* default
        long realListLength
        long elementSize

    cdef void* get(self, long index)
