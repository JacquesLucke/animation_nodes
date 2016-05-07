
from libc.stdlib cimport malloc, free, realloc
from libc.string cimport memcpy
from libc.math cimport sin
cimport cython

ctypedef fused list_or_tuple:
    list
    tuple

cdef class FloatListIterator:
    cdef:
        FloatList source
        long current

    def __cinit__(self, FloatList source):
        self.source = source
        self.current = 0

    def __next__(self):
        if self.current >= self.source.length:
            raise StopIteration()
        cdef float currentValue = self.source.data[self.current]
        self.current += 1
        return currentValue

@cython.freelist(10)
cdef class FloatList:
    cdef:
        float* data
        long length
        long allocated

    def __cinit__(self, long length = 0, long allocate = -1):
        if length < 0:
            raise Exception("Length has to be >= 0")
        if allocate < length:
            allocate = length
        self.data = <float*>malloc(sizeof(float) * allocate)
        if self.data == NULL:
            raise MemoryError()

        self.length = length
        self.allocated = allocate

    def __dealloc__(self):
        if self.data != NULL:
            free(self.data)

    cdef void _resize(self, long newSize):
        self.data = <float*>realloc(self.data, sizeof(float) * newSize)
        if self.data == NULL:
            self.length = 0
            self.allocated = 0
            raise MemoryError()
        self.allocated = newSize

    def __len__(self):
        return self.length

    cpdef fill(self, float value):
        cdef long i
        for i in range(self.length):
            self.data[i] = value

    cpdef append(self, float value):
        if self.length == self.allocated:
            self._resize(<long>(self.allocated * 1.5) + 1)
        self.data[self.length] = value
        self.length += 1

    cpdef extend(self, list_or_tuple values):
        cdef long newLength = self.length + len(values)
        if newLength > self.allocated:
            self._resize(<long>(newLength * 1.2))
        cdef long i
        for i, value in enumerate(values, start = self.length):
            self.data[i] = value
        self.length = newLength

    cpdef float[:] getMemoryView(self):
        if self.length > 0:
            return <float[:self.length]>self.data
        else:
            return (<float[:1]>self.data)[1:]

    cpdef float[:] getSlicedMemoryView(self, sliceObject):
        cdef long start, stop, step
        start, stop, step = sliceObject.indices(self.length)
        return self.getMemoryView()[start:stop:step]

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.getMemoryView()[key]
        else:
            return self.getSlice(key)

    cpdef FloatList getSlice(self, sliceObject):
        cdef float[:] memView = self.getSlicedMemoryView(sliceObject)
        newList = FloatList(len(memView))
        cdef int i
        for i in range(len(memView)):
            newList.data[i] = memView[i]
        return newList

    def __setitem__(self, key, value):
        if isinstance(key, int):
            self.getMemoryView()[key] = value
        else:
            start, stop, step = key.indices(self.length)
            self.getMemoryView()[start:stop:step] = value

    cpdef copy(self):
        newList = FloatList(self.length)
        newList.overwrite(self)
        return newList

    cpdef long index(self, float value):
        cdef long i
        for i in range(self.length):
            if self.data[i] == value:
                return i
        return -1

    cpdef long count(self, float value):
        cdef long i
        cdef long amount = 0
        for i in range(self.length):
            if self.data[i] == value:
                amount += 1
        return amount

    cpdef FloatList reversed(self):
        cdef:
            FloatList newList = FloatList(self.length)
            long i, offset
        offset = self.length - 1
        for i in range(self.length):
            newList.data[i] = self.data[offset - i]
        return newList

    def __add__(FloatList a, FloatList b):
        return FloatList.join(a, b)

    def __mul__(FloatList self, long amount):
        cdef FloatList newList = FloatList(self.length * amount)
        cdef long i
        for i in range(amount):
            newList.overwrite(self, self.length * i)
        return newList

    def __iadd__(self, FloatList other):
        if self.length + other.length > self.allocated:
            self._resize(self.length + other.length)
        self.overwrite(other, index = self.length)
        return self

    def __iter__(self):
        return FloatListIterator(self)

    def __contains__(self, float value):
        cdef long i
        for i in range(self.length):
            if self.data[i] == value:
                return True
        return False

    cpdef overwrite(self, FloatList other, long index = 0):
        if index + other.length > self.allocated:
            self._resize(index + other.length)
        memcpy(self.data + index, other.data, other.length * sizeof(float))
        self.length = max(self.length, index + other.length)

    @classmethod
    def join(cls, *sourceLists):
        cdef long newLength = 0
        cdef long offset = 0
        cdef FloatList source

        for source in sourceLists:
            newLength += len(source)
        newList = FloatList(newLength)
        for source in sourceLists:
            newList.overwrite(source, offset)
            offset += source.length

        return newList

    @classmethod
    def fromValues(cls, list_or_tuple values):
        newList = FloatList(len(values))
        cdef long i
        for i, value in enumerate(values):
            newList.data[i] = value
        return newList

    def __repr__(self):
        return "<FloatList {}>".format(list(self.getMemoryView()))

    def status(self):
        return "Length: {}, Allocated: {}, Size: {} bytes".format(
            self.length, self.allocated, self.allocated * sizeof(float))


cdef class DoubleListIterator:
    cdef:
        DoubleList source
        long current

    def __cinit__(self, DoubleList source):
        self.source = source
        self.current = 0

    def __next__(self):
        if self.current >= self.source.length:
            raise StopIteration()
        cdef double currentValue = self.source.data[self.current]
        self.current += 1
        return currentValue

@cython.freelist(10)
cdef class DoubleList:
    cdef:
        double* data
        long length
        long allocated

    def __cinit__(self, long length = 0, long allocate = -1):
        if length < 0:
            raise Exception("Length has to be >= 0")
        if allocate < length:
            allocate = length
        self.data = <double*>malloc(sizeof(double) * allocate)
        if self.data == NULL:
            raise MemoryError()

        self.length = length
        self.allocated = allocate

    def __dealloc__(self):
        if self.data != NULL:
            free(self.data)

    cdef void _resize(self, long newSize):
        self.data = <double*>realloc(self.data, sizeof(double) * newSize)
        if self.data == NULL:
            self.length = 0
            self.allocated = 0
            raise MemoryError()
        self.allocated = newSize

    def __len__(self):
        return self.length

    cpdef fill(self, double value):
        cdef long i
        for i in range(self.length):
            self.data[i] = value

    cpdef append(self, double value):
        if self.length == self.allocated:
            self._resize(<long>(self.allocated * 1.5) + 1)
        self.data[self.length] = value
        self.length += 1

    cpdef extend(self, list_or_tuple values):
        cdef long newLength = self.length + len(values)
        if newLength > self.allocated:
            self._resize(<long>(newLength * 1.2))
        cdef long i
        for i, value in enumerate(values, start = self.length):
            self.data[i] = value
        self.length = newLength

    cpdef double[:] getMemoryView(self):
        if self.length > 0:
            return <double[:self.length]>self.data
        else:
            return (<double[:1]>self.data)[1:]

    cpdef double[:] getSlicedMemoryView(self, sliceObject):
        cdef long start, stop, step
        start, stop, step = sliceObject.indices(self.length)
        return self.getMemoryView()[start:stop:step]

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.getMemoryView()[key]
        else:
            return self.getSlice(key)

    cpdef DoubleList getSlice(self, sliceObject):
        cdef double[:] memView = self.getSlicedMemoryView(sliceObject)
        newList = DoubleList(len(memView))
        cdef int i
        for i in range(len(memView)):
            newList.data[i] = memView[i]
        return newList

    def __setitem__(self, key, value):
        if isinstance(key, int):
            self.getMemoryView()[key] = value
        else:
            start, stop, step = key.indices(self.length)
            self.getMemoryView()[start:stop:step] = value

    cpdef copy(self):
        newList = DoubleList(self.length)
        newList.overwrite(self)
        return newList

    cpdef long index(self, double value):
        cdef long i
        for i in range(self.length):
            if self.data[i] == value:
                return i
        return -1

    cpdef long count(self, double value):
        cdef long i
        cdef long amount = 0
        for i in range(self.length):
            if self.data[i] == value:
                amount += 1
        return amount

    cpdef DoubleList reversed(self):
        cdef:
            DoubleList newList = DoubleList(self.length)
            long i, offset
        offset = self.length - 1
        for i in range(self.length):
            newList.data[i] = self.data[offset - i]
        return newList

    def __add__(DoubleList a, DoubleList b):
        return DoubleList.join(a, b)

    def __mul__(DoubleList self, long amount):
        cdef DoubleList newList = DoubleList(self.length * amount)
        cdef long i
        for i in range(amount):
            newList.overwrite(self, self.length * i)
        return newList

    def __iadd__(self, DoubleList other):
        if self.length + other.length > self.allocated:
            self._resize(self.length + other.length)
        self.overwrite(other, index = self.length)
        return self

    def __iter__(self):
        return DoubleListIterator(self)

    def __contains__(self, double value):
        cdef long i
        for i in range(self.length):
            if self.data[i] == value:
                return True
        return False

    cpdef overwrite(self, DoubleList other, long index = 0):
        if index + other.length > self.allocated:
            self._resize(index + other.length)
        memcpy(self.data + index, other.data, other.length * sizeof(double))
        self.length = max(self.length, index + other.length)

    @classmethod
    def join(cls, *sourceLists):
        cdef long newLength = 0
        cdef long offset = 0
        cdef DoubleList source

        for source in sourceLists:
            newLength += len(source)
        newList = DoubleList(newLength)
        for source in sourceLists:
            newList.overwrite(source, offset)
            offset += source.length

        return newList

    @classmethod
    def fromValues(cls, list_or_tuple values):
        newList = DoubleList(len(values))
        cdef long i
        for i, value in enumerate(values):
            newList.data[i] = value
        return newList

    def __repr__(self):
        return "<DoubleList {}>".format(list(self.getMemoryView()))

    def status(self):
        return "Length: {}, Allocated: {}, Size: {} bytes".format(
            self.length, self.allocated, self.allocated * sizeof(double))

    @classmethod
    def fromRange(cls, long amount, double start, double step):
        cdef DoubleList newList = DoubleList(max(0, amount))
        cdef long i
        for i in range(max(0, amount)):
            newList.data[i] = start + i * step
        return newList


cdef class IntegerListIterator:
    cdef:
        IntegerList source
        long current

    def __cinit__(self, IntegerList source):
        self.source = source
        self.current = 0

    def __next__(self):
        if self.current >= self.source.length:
            raise StopIteration()
        cdef long long currentValue = self.source.data[self.current]
        self.current += 1
        return currentValue

@cython.freelist(10)
cdef class IntegerList:
    cdef:
        long long* data
        long length
        long allocated

    def __cinit__(self, long length = 0, long allocate = -1):
        if length < 0:
            raise Exception("Length has to be >= 0")
        if allocate < length:
            allocate = length
        self.data = <long long*>malloc(sizeof(long long) * allocate)
        if self.data == NULL:
            raise MemoryError()

        self.length = length
        self.allocated = allocate

    def __dealloc__(self):
        if self.data != NULL:
            free(self.data)

    cdef void _resize(self, long newSize):
        self.data = <long long*>realloc(self.data, sizeof(long long) * newSize)
        if self.data == NULL:
            self.length = 0
            self.allocated = 0
            raise MemoryError()
        self.allocated = newSize

    def __len__(self):
        return self.length

    cpdef fill(self, long long value):
        cdef long i
        for i in range(self.length):
            self.data[i] = value

    cpdef append(self, long long value):
        if self.length == self.allocated:
            self._resize(<long>(self.allocated * 1.5) + 1)
        self.data[self.length] = value
        self.length += 1

    cpdef extend(self, list_or_tuple values):
        cdef long newLength = self.length + len(values)
        if newLength > self.allocated:
            self._resize(<long>(newLength * 1.2))
        cdef long i
        for i, value in enumerate(values, start = self.length):
            self.data[i] = value
        self.length = newLength

    cpdef long long[:] getMemoryView(self):
        if self.length > 0:
            return <long long[:self.length]>self.data
        else:
            return (<long long[:1]>self.data)[1:]

    cpdef long long[:] getSlicedMemoryView(self, sliceObject):
        cdef long start, stop, step
        start, stop, step = sliceObject.indices(self.length)
        return self.getMemoryView()[start:stop:step]

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.getMemoryView()[key]
        else:
            return self.getSlice(key)

    cpdef IntegerList getSlice(self, sliceObject):
        cdef long long[:] memView = self.getSlicedMemoryView(sliceObject)
        newList = IntegerList(len(memView))
        cdef int i
        for i in range(len(memView)):
            newList.data[i] = memView[i]
        return newList

    def __setitem__(self, key, value):
        if isinstance(key, int):
            self.getMemoryView()[key] = value
        else:
            start, stop, step = key.indices(self.length)
            self.getMemoryView()[start:stop:step] = value

    cpdef copy(self):
        newList = IntegerList(self.length)
        newList.overwrite(self)
        return newList

    cpdef long index(self, long long value):
        cdef long i
        for i in range(self.length):
            if self.data[i] == value:
                return i
        return -1

    cpdef long count(self, long long value):
        cdef long i
        cdef long amount = 0
        for i in range(self.length):
            if self.data[i] == value:
                amount += 1
        return amount

    cpdef IntegerList reversed(self):
        cdef:
            IntegerList newList = IntegerList(self.length)
            long i, offset
        offset = self.length - 1
        for i in range(self.length):
            newList.data[i] = self.data[offset - i]
        return newList

    def __add__(IntegerList a, IntegerList b):
        return IntegerList.join(a, b)

    def __mul__(IntegerList self, long amount):
        cdef IntegerList newList = IntegerList(self.length * amount)
        cdef long i
        for i in range(amount):
            newList.overwrite(self, self.length * i)
        return newList

    def __iadd__(self, IntegerList other):
        if self.length + other.length > self.allocated:
            self._resize(self.length + other.length)
        self.overwrite(other, index = self.length)
        return self

    def __iter__(self):
        return IntegerListIterator(self)

    def __contains__(self, long long value):
        cdef long i
        for i in range(self.length):
            if self.data[i] == value:
                return True
        return False

    cpdef overwrite(self, IntegerList other, long index = 0):
        if index + other.length > self.allocated:
            self._resize(index + other.length)
        memcpy(self.data + index, other.data, other.length * sizeof(long long))
        self.length = max(self.length, index + other.length)

    @classmethod
    def join(cls, *sourceLists):
        cdef long newLength = 0
        cdef long offset = 0
        cdef IntegerList source

        for source in sourceLists:
            newLength += len(source)
        newList = IntegerList(newLength)
        for source in sourceLists:
            newList.overwrite(source, offset)
            offset += source.length

        return newList

    @classmethod
    def fromValues(cls, list_or_tuple values):
        newList = IntegerList(len(values))
        cdef long i
        for i, value in enumerate(values):
            newList.data[i] = value
        return newList

    def __repr__(self):
        return "<IntegerList {}>".format(list(self.getMemoryView()))

    def status(self):
        return "Length: {}, Allocated: {}, Size: {} bytes".format(
            self.length, self.allocated, self.allocated * sizeof(long long))



cpdef DoubleList floatListToDoubleList(FloatList floatList):
    cdef DoubleList newList = DoubleList(floatList.length)
    cdef long i
    for i in range(len(floatList)):
        newList.data[i] = floatList.data[i]
    return newList


'''
Lists have to support the following operations:
    myList.append(baseType)
    myList.extend(baseTypeList)
    myList.fill(baseType)
    list.join(*lists)
    list.fromValues(baseTypeList)
    len(myList)                     # __len__
    myList + otherList              # __add__
    myList += otherList             # __iadd__
    myList * x                      # __mul__
    myList[x]  | myList[x:y:z]      # __getitem__
    myList = x | myList[x:y:z] = x  # __setitem__
    x in myList                     # __contains__
'''