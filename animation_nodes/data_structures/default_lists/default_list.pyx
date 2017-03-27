cdef class DefaultList:
    cdef long getRealLength(self):
        return 0

    @classmethod
    def getMaxLength(cls, *args):
        cdef:
            DefaultList defaultList
            long maxLength = 0
            long length

        for defaultList in args:
            length = defaultList.getRealLength()
            if length > maxLength:
                maxLength = length
        return maxLength
