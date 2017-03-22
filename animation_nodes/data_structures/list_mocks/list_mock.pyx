cdef class ListMock:
    cdef long getSuggestedLength(self):
        return 0

    @classmethod
    def getMaxLength(cls, *args):
        cdef:
            ListMock listMock
            long maxLength = 0
            long length

        for listMock in args:
            length = listMock.getSuggestedLength()
            if length > maxLength:
                maxLength = length
        return maxLength
