from .. lists.clist cimport CList

cdef class VirtualList:
    pass

cdef class VirtualPyList(VirtualList):
    pass

cdef class VirtualPyList_Element_NoCopy(VirtualPyList):
    cdef object element

cdef class VirtualPyList_Element_Copy(VirtualPyList):
    cdef object element
    cdef object copy

cdef class VirtualPyList_List_NoCopy(VirtualPyList):
    cdef list realList
    cdef Py_ssize_t realLength

cdef class VirtualPyList_List_Copy(VirtualPyList):
    cdef list realList
    cdef Py_ssize_t realLength
    cdef object copy
