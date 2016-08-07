cdef class PolygonIndicesList:
    def __cinit__(self, long indicesAmount = 0, long loopAmount = 0):
        self.indices = UIntegerList(length = indicesAmount)
        self.loopStarts = IntegerList(length = loopAmount)
        self.loopLengths = IntegerList(length = loopAmount)


    # Special Methods for Python
    ###############################################

    def __len__(self):
        return self.getLength()

    cdef long getLength(self):
        return self.loopStarts.length

    # Base operations for lists - mimic python list
    ###############################################

    cpdef append(self, value):
        if not self.isValueValid(value):
            raise TypeError("cannot append value to this list")

        self.loopStarts.append(self.indices.length)
        self.loopLengths.append(len(value))
        self.indices.extend(value)

    cdef isValueValid(self, value):
        return len(value) >= 3 and all(v >= 0 and isinstance(v, int) for v in value)

    cpdef extend(self, values):
        for value in values:
            self.append(value)


    # Classmethods for List Creation
    ###############################################

    @classmethod
    def fromValues(cls, values):
        cdef PolygonIndicesList newList = PolygonIndicesList()
        newList.extend(values)
        return newList
