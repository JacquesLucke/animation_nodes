cdef class VirtualList:
    @classmethod
    def getMaxLength(cls, *args):
        return max(obj.getRealLength() for obj in args)

    def getRealLength(self):
        return 0

ctypedef fused PyListOrElement:
    list
    object

cdef class VirtualPyList(VirtualList):
    @classmethod
    def fromListOrElement(cls, PyListOrElement obj, object default, copy = None):
        if PyListOrElement is list:
            return cls.fromList(obj, default, copy)
        else:
            return cls.fromElement(obj, copy)

    @classmethod
    def fromList(cls, realList, default, copy = None):
        if len(realList) == 0:
            return cls.fromElement(default, copy)
        elif len(realList) == 1:
            return cls.fromElement(realList[0], copy, realLength = 1)
        else:
            if copy is None:
                return VirtualPyList_List_NoCopy(realList)
            else:
                return VirtualPyList_List_Copy(realList, copy)

    @classmethod
    def fromElement(cls, object element, copy = None, realLength = 0):
        if copy is None:
            return VirtualPyList_Element_NoCopy(element, realLength)
        else:
            return VirtualPyList_Element_Copy(element, copy, realLength)

cdef class VirtualPyList_Element_NoCopy(VirtualPyList):
    cdef object element
    cdef Py_ssize_t realLength

    def __cinit__(self, object element, Py_ssize_t realLength = 0):
        self.element = element
        self.realLength = 0

    def __getitem__(self, index):
        return self.element

    def getRealLength(self):
        return self.realLength

cdef class VirtualPyList_Element_Copy(VirtualPyList):
    cdef object element
    cdef object copy
    cdef Py_ssize_t realLength

    def __cinit__(self, object element, copy, Py_ssize_t realLength = 0):
        self.element = element
        self.copy = copy
        self.realLength = realLength

    def __getitem__(self, index):
        return self.copy(self.element)

    def getRealLength(self):
        return self.realLength

cdef class VirtualPyList_List_NoCopy(VirtualPyList):
    cdef object realList
    cdef Py_ssize_t realLength

    def __cinit__(self, realList):
        self.realList = realList
        self.realLength = len(realList)
        assert self.realLength > 0

    def __getitem__(self, Py_ssize_t index):
        return self.realList[index % self.realLength]

    def getRealLength(self):
        return self.realLength

cdef class VirtualPyList_List_Copy(VirtualPyList):
    cdef object realList
    cdef Py_ssize_t realLength
    cdef object copy

    def __cinit__(self, realList, copy):
        self.realList = realList
        self.realLength = len(realList)
        self.copy = copy
        assert self.realLength > 0

    def __getitem__(self, Py_ssize_t index):
        return self.copy(self.realList[index % self.realLength])

    def getRealLength(self):
        return self.realLength
