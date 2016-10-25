from .. lists.clist cimport CList

cdef class CListMock:
    def __cinit__(self, dataType, listOrElement, defaultElement):
        if not issubclass(dataType, CList):
            raise TypeError("first argument has to be a subclass of CList")

        if isinstance(listOrElement, dataType):
            self.realList = listOrElement
            self.arrayStart = <char*>self.realList.getPointer()
            self.elementSize = self.realList.getElementSize()
            self.realListLength = self.realList.getLength()
            self.defaultElementList = dataType.fromValues([defaultElement])
        else:
            self.realList = None
            self.elementSize = 0
            self.arrayStart = NULL
            self.realListLength = 0
            self.defaultElementList = dataType.fromValues([listOrElement])

        self.default = self.defaultElementList.getPointer()

    def __getitem__(self, long index):
        if 0 <= index < self.realListLength:
            return self.realList[index]
        return self.defaultElementList[0]

    cdef void* get(self, long index):
        if 0 <= index < self.realListLength:
            return self.arrayStart + index * self.elementSize
        return self.default

    cdef long getSuggestedLength(self):
        return self.realListLength
