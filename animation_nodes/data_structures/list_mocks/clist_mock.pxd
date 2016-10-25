from . list_mock cimport ListMock
from .. lists.clist cimport CList

cdef class CListMock(ListMock):
    cdef:
        object dataType
        CList realList
        CList defaultElementList

        char* arrayStart
        void* default
        long realListLength
        long elementSize

    cdef void* get(self, long index)
