cdef class PolygonIndicesList:
    def __cinit__(self, long indicesAmount = 0, long loopAmount = 0):
        self.indices = UIntegerList(length = indicesAmount)
        self.loopStarts = UIntegerList(length = loopAmount)
        self.loopLengths = UIntegerList(length = loopAmount)


    # Special Methods for Python
    ###############################################

    def __len__(self):
        return self.getLength()

    cdef long getLength(self):
        return self.loopStarts.length

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.getElementAtIndex(key)
        raise TypeError("expected int")

    def __iter__(self):
        return PolygonIndicesListIterator(self)


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

    cpdef copy(self):
        cdef PolygonIndicesList newList = PolygonIndicesList()
        newList.indices.overwrite(self.indices)
        newList.loopStarts.overwrite(self.loopStarts)
        newList.loopLengths.overwrite(self.loopLengths)
        return newList


    # Utilities for setting and getting
    ###############################################

    cdef getElementAtIndex(self, long index):
        index = self.tryCorrectIndex(index)
        cdef long start = self.loopStarts.data[index]
        cdef long length = self.loopLengths.data[index]
        return tuple(self.indices.data[i] for i in range(start, start + length))

    cdef tryCorrectIndex(self, long index):
        if index < 0:
            index += self.getLength()
        if index < 0 or index >= self.getLength():
            raise IndexError("list index out of range")
        return index

    def copyWithNewOrder(self, ULongList newOrder):
        cdef PolygonIndicesList newList = PolygonIndicesList()
        cdef long i
        for i in newOrder:
            newList.append(self.getElementAtIndex(i))
        return newList


    # Create new lists based on an existing list
    ###############################################

    def reversed(self):
        cdef long length = self.getLength()
        cdef ULongList newOrder = ULongList(length = length)
        for i in range(length):
            newOrder.data[i] = length - i - 1
        return self.copyWithNewOrder(newOrder)


    # Classmethods for List Creation
    ###############################################

    @classmethod
    def fromValues(cls, values):
        cdef PolygonIndicesList newList = PolygonIndicesList()
        newList.extend(values)
        return newList

    @classmethod
    def join(cls, *lists):
        cdef PolygonIndicesList newList = PolygonIndicesList()
        for elements in lists:
            newList.extend(elements)
        return newList


cdef class PolygonIndicesListIterator:
    cdef:
        PolygonIndicesList source
        long current

    def __cinit__(self, PolygonIndicesList source):
        self.source = source
        self.current = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.current >= self.source.getLength():
            raise StopIteration()
        self.current += 1
        return self.source[self.current - 1]
