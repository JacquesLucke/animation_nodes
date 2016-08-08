from libc.string cimport memcpy

cdef class PolygonIndicesList:
    def __cinit__(self, long indicesAmount = 0, long loopAmount = 0):
        self.indices = UIntegerList(length = indicesAmount)
        self.polyStarts = UIntegerList(length = loopAmount)
        self.polyLengths = UIntegerList(length = loopAmount)


    # Special Methods for Python
    ###############################################

    def __len__(self):
        return self.getLength()

    cdef long getLength(self):
        return self.polyStarts.length

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.getElementAtIndex(key)
        elif isinstance(key, slice):
            return self.getValuesInSlice(key)
        raise TypeError("expected int or slice")

    def __iter__(self):
        return PolygonIndicesListIterator(self)


    # Base operations for lists - mimic python list
    ###############################################

    cpdef append(self, value):
        if not self.isValueValid(value):
            raise TypeError("cannot append value to this list")

        self.polyStarts.append(self.indices.length)
        self.polyLengths.append(len(value))
        self.indices.extend(value)

    cdef isValueValid(self, value):
        return len(value) >= 3 and all(v >= 0 and isinstance(v, int) for v in value)

    cpdef extend(self, values):
        if isinstance(values, PolygonIndicesList):
            self.extend_SameType(values)
        else:
            for value in values:
                self.append(value)

    cdef extend_SameType(self, PolygonIndicesList otherList):
        cdef long oldLength = self.getLength()
        cdef long oldIndicesLength = self.indices.length
        self.indices.extend(otherList.indices)
        self.polyStarts.extend(otherList.polyStarts)
        self.polyLengths.extend(otherList.polyLengths)

        cdef long i
        for i in range(otherList.getLength()):
            self.polyStarts.data[oldLength + i] += oldIndicesLength

    cpdef copy(self):
        cdef PolygonIndicesList newList = PolygonIndicesList()
        newList.indices.overwrite(self.indices)
        newList.polyStarts.overwrite(self.polyStarts)
        newList.polyLengths.overwrite(self.polyLengths)
        return newList


    # Utilities for setting and getting
    ###############################################

    cdef getElementAtIndex(self, long index):
        index = self.tryCorrectIndex(index)
        cdef long start = self.polyStarts.data[index]
        cdef long length = self.polyLengths.data[index]
        return tuple(self.indices.data[i] for i in range(start, start + length))

    cdef tryCorrectIndex(self, long index):
        if index < 0:
            index += self.getLength()
        if index < 0 or index >= self.getLength():
            raise IndexError("list index out of range")
        return index

    cdef getValuesInSlice(self, slice sliceObject):
        cdef ULongList order = ULongList.fromValues(range(*sliceObject.indices(self.getLength())))
        return self.copyWithNewOrder(order, checkIndices = False)

    cpdef copyWithNewOrder(self, ULongList newOrder, checkIndices = True):
        if checkIndices:
            if newOrder.length == 0:
                return PolygonIndicesList()
            if self.getLength() == 0:
                raise IndexError("Not all indices in the new order exist")
            else:
                if newOrder.getMaxValue() >= self.getLength():
                    raise IndexError("Not all indices in the new order exist")

        cdef long i
        cdef long indicesAmount = 0
        for i in range(newOrder.length):
            indicesAmount += self.polyLengths.data[newOrder.data[i]]

        cdef PolygonIndicesList newList = PolygonIndicesList(
                indicesAmount = indicesAmount,
                loopAmount = newOrder.length)

        cdef long index, length, start, accumulatedLength = 0
        for i in range(newOrder.length):
            index = newOrder.data[i]

            length = self.polyLengths.data[index]
            start = self.polyStarts.data[index]

            newList.polyLengths.data[i] = length
            newList.polyStarts.data[i] = accumulatedLength
            memcpy(newList.indices.data + accumulatedLength,
                   self.indices.data + start,
                   sizeof(unsigned int) * length)
            accumulatedLength += length
        return newList


    # Create new lists based on an existing list
    ###############################################

    def reversed(self):
        cdef long i, length = self.getLength()
        cdef ULongList newOrder = ULongList(length = length)
        for i in range(length):
            newOrder.data[i] = length - i - 1
        return self.copyWithNewOrder(newOrder, checkIndices = False)


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

    def __repr__(self):
        return "<PolygonIndicesList {}>".format(list(self[i] for i in range(self.getLength())))


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
