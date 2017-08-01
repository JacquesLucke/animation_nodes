cdef class VirtualList:
    pass

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
    def fromList(cls, list realList, default, copy = None):
        if len(realList) == 0:
            return cls.fromElement(default, copy)
        else:
            if copy is None:
                return VirtualPyList_List_NoCopy(realList)
            else:
                return VirtualPyList_List_Copy(realList, copy)

    @classmethod
    def fromElement(cls, object element, copy = None):
        if copy is None:
            return VirtualPyList_Element_NoCopy(element)
        else:
            return VirtualPyList_Element_Copy(element, copy)

cdef class VirtualPyList_Element_NoCopy(VirtualPyList):
    def __cinit__(self, object element):
        self.element = element

    def __getitem__(self, index):
        return self.element

cdef class VirtualPyList_Element_Copy(VirtualPyList):
    def __cinit__(self, object element, copy):
        self.element = element
        self.copy = copy

    def __getitem__(self, index):
        return self.copy(self.element)

cdef class VirtualPyList_List_NoCopy(VirtualPyList):
    def __cinit__(self, list realList):
        self.realList = realList
        self.realLength = len(realList)
        assert self.realLength > 0

    def __getitem__(self, Py_ssize_t index):
        return self.realList[index % self.realLength]

cdef class VirtualPyList_List_Copy(VirtualPyList):
    def __cinit__(self, list realList, copy):
        self.realList = realList
        self.realLength = len(realList)
        self.copy = copy
        assert self.realLength > 0

    def __getitem__(self, Py_ssize_t index):
        return self.copy(self.realList[index % self.realLength])
